import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from smartx_rfid.utils.path import get_prefix_from_path

from app.services.tray import tray_manager
from app.services.settings_service import settings_service
from app.schemas.application import SettingsSchema
from app.core import settings

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


async def delayed_func(func, delay: float = 1.0):
	await asyncio.sleep(delay)
	func()


@router.post('/restart_application')
async def restart_application():
	asyncio.create_task(delayed_func(tray_manager.restart_application))
	return JSONResponse(content={'status': 'restarting'})


@router.post('/exit_application')
async def exit_application():
	asyncio.create_task(delayed_func(tray_manager.exit_application))
	return JSONResponse(content={'status': 'exiting'})


@router.get('/get_current_settings', summary='Get the current application settings')
async def get_current_settings():
	return JSONResponse(content=settings.get_current_settings())


@router.post(
	'/update_settings',
	summary='Update the current application settings',
	description='Update the current application settings with the provided data',
)
async def update_settings(settings_data: SettingsSchema):  # type: ignore
	settings_service.update_settings(settings_data.model_dump(exclude_unset=True))
	return JSONResponse(content={'status': 'updated', 'settings': settings.get_current_settings()})


@router.post('/create_device/{device_name}', summary='Create a new device configuration')
async def create_device(device_name: str, data: dict):
	success, error = settings_service.create_device(device_name, data)
	if success:
		return JSONResponse(content={'status': 'created', 'device': device_name})
	return JSONResponse(content={'status': 'error', 'message': error}, status_code=400)


@router.put('/update_device/{device_name}', summary='Update an existing device configuration')
async def update_device(device_name: str, data: dict):
	success, error = settings_service.update_device(device_name, data)
	if success:
		return JSONResponse(content={'status': 'updated', 'device': device_name})
	return JSONResponse(content={'status': 'error', 'message': error}, status_code=400)


@router.delete('/delete_device/{device_name}', summary='Delete a device configuration')
async def delete_device(device_name: str):
	success, error = settings_service.delete_device(device_name)
	if success:
		return JSONResponse(content={'status': 'deleted', 'device': device_name})
	return JSONResponse(content={'status': 'error', 'message': error}, status_code=400)


@router.get('/has_changes', summary='Check if there are unsaved changes in the settings')
async def has_changes():
	return JSONResponse(content={'has_changes': settings_service.has_changes})


@router.get('/get_application_config_example', summary='Get the example configuration')
async def get_application_config_example():
	return JSONResponse(content=settings_service._get_example_config())
