// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the CONNECT_DLL_EXPORTS
// symbol defined on the command line. This symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// CONNECT_DLL_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef CONNECT_DLL_EXPORTS
#define CONNECT_DLL_API __declspec(dllexport)
#else
#define CONNECT_DLL_API __declspec(dllimport)
#endif

#include <visa.h>


typedef struct {
	int touched;
	float x, y;
} touch_info;

extern "C" {

	//-- Create a ResourceManager object
	CONNECT_DLL_API ViSession create_resource_manager();

	//-- Cleanup a ResourceManager created by create_resource_manager()
	CONNECT_DLL_API void cleanup_resource_manager(ViSession resource_mgr);

	//-- Connect with the TSC device. Returns a pointer to the device (resource)
	CONNECT_DLL_API ViSession connect(ViSession resource_mgr, char *resource_name);

	//-- Disconnect from the device. 
	//-- Argument: a device created by connect()
	CONNECT_DLL_API void disconnect(ViSession resource);

	//-- Get touch information from the device.
	//-- Argument: a device created by connect()
	CONNECT_DLL_API touch_info get_touch_info(ViSession resource);
}
