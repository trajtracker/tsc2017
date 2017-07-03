// connect_dll.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "connect_dll.h"
#include <stdio.h>
#include <windows.h>      
#include <mutex>


//==================================================================================================
//            Resource manager
//==================================================================================================

//-------------------------------------------------------------------------------------
//-- Create a ResourceManager object
CONNECT_DLL_API ViSession create_resource_manager()
{
	ViSession resource_mgr;
	ViStatus status = viOpenDefaultRM(&resource_mgr);
	if (status < VI_SUCCESS)
	{
		printf("Unable to open the Resource Manager.\n");
		return 0;
	}

	return resource_mgr;
}

//-------------------------------------------------------------------------------------
//-- Cleanup a ResourceManager created by create_resource_manager()
CONNECT_DLL_API void cleanup_resource_manager(ViSession resource_mgr)
{
	viClose(resource_mgr);
}


//==================================================================================================
//            Data of events from the device
//==================================================================================================

void swap_bytes_of(unsigned short *num)
{
	uint8_t *high_byte = (uint8_t *)num;
	uint8_t *low_byte = high_byte + 1;
	uint8_t temp;

	temp = *high_byte;
	*high_byte = *low_byte;
	*low_byte = temp;
}


//-- Keep the data received in an event
class EventInfo {
public:
	ViInt16 nbytes;
	unsigned char data[256];

	EventInfo();

	bool clicked();
	unsigned short x();
	unsigned short y();
};

EventInfo::EventInfo()
{
	this->nbytes = 0;
}


bool EventInfo::clicked()
{
	return data[1] == 0;
}

unsigned short EventInfo::x()
{
	unsigned short n = *((unsigned short *)(data + 2));
	swap_bytes_of(&n);
	return n;
}

unsigned short EventInfo::y()
{
	unsigned short n = *((unsigned short *)(data + 4));
	swap_bytes_of(&n);
	return n;
}

//-- The last event received from the device
static EventInfo last_event;


//==================================================================================================
//            Communicate with the device
//==================================================================================================

std::mutex lock;


//-------------------------------------------------------------------------------------
//-- Try connecting with a specific device
static ViSession try_connect(ViSession resource_mgr, char *resource_name)
{
	ViSession resource;
	ViStatus status = viOpen(resource_mgr, resource_name, VI_NULL, VI_NULL, &resource);
	return status < VI_SUCCESS ? 0 : resource;
}


//-------------------------------------------------------------------------------------
ViStatus _VI_FUNCH event_handler(ViSession instr, ViEventType etype,
	ViEvent event, ViAddr userhandle)
{
	EventInfo data;

	//-- Get the size of this event (should be 40 bytes)

	ViStatus status = viGetAttribute(event, VI_ATTR_USB_RECV_INTR_SIZE, &data.nbytes);
	if (status < VI_SUCCESS) {
		printf("Failed getting VI_ATTR_USB_RECV_INTR_SIZE, event ignored\n");
		return status;
	}
	if (data.nbytes > 256) {
		printf("Data too long, ignored");
		return VI_SUCCESS;
	}

	//-- get the actual data from the event
	status = viGetAttribute(event, VI_ATTR_USB_RECV_INTR_DATA, data.data);
	if (status < VI_SUCCESS) {
		printf("Failed getting VI_ATTR_USB_RECV_INTR_DATA, event ignored\n");
		return status;
	}

	//-- Store the data
	lock.lock();  // lock to prevent confusions with other threads (other event handlers + calls to the DLL)
	last_event.nbytes = data.nbytes;
	memcpy((void*)last_event.data, data.data, 256);
	lock.unlock();

	return VI_SUCCESS;
}


//-------------------------------------------------------------------------------------
//-- Connect with the TSC device. Returns a pointer to the device
CONNECT_DLL_API ViSession connect(ViSession resource_mgr, char *resource_name)
{
	//-- Connect to the resource
	ViSession resource = try_connect(resource_mgr, resource_name);
	if (resource == NULL)
	{
		printf("Failed connecting to the device %s\n", resource_name);
		return 0;
	}

	//-- Register the event handler
	ViStatus status = viInstallHandler(resource, VI_EVENT_USB_INTR, event_handler, (ViAddr)12345678);
	if (status < VI_SUCCESS)
	{
		printf("Could not install the interrupt handler\n");
		viClose(resource);
		return NULL;
	}

	//-- Enable the interrupt event
	status = viEnableEvent(resource, VI_EVENT_USB_INTR, VI_HNDLR, VI_NULL);
	if (status < VI_SUCCESS)
	{
		printf("Could not enable the interrupt event for %s, status=%d\n", resource_name, status);
		viClose(resource);
		return 0;
	}

	return resource;
}


//-------------------------------------------------------------------------------------
//-- Disconnect from the device. 
//-- Argument: a device created by connect()
CONNECT_DLL_API void disconnect(ViSession resource)
{
	viClose(resource);
}


//-------------------------------------------------------------------------------------
//-- Get touch information from the device.
//-- Argument: a device created by connect()
CONNECT_DLL_API touch_info get_touch_info(ViSession resource)
{
	touch_info ti = {0, 0, 0, 0};

	if (last_event.nbytes == 0)
	{
		return ti;
	}

	ti.valid = 1;
	ti.touched = last_event.clicked();
	ti.x = last_event.x();
	ti.y = last_event.y();

	return ti;
}
