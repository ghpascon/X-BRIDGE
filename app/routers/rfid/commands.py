from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.path import get_prefix_from_path
from app.schemas.api.device import validate_device
from app.schemas.devices import devices

router = APIRouter(
    prefix=get_prefix_from_path(__file__), tags=[get_prefix_from_path(__file__)]
)


@router.post("/start/{device}")
async def start_inventory(device: str):
    try:
        status, msg = validate_device(device=device)
        if not status:
            print("[ START ]", msg)
            raise HTTPException(status_code=422, detail=msg)

        print(f"START -> {device}")
        await devices.start_inventory(device)
        return {"msg": msg}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": e})


@router.post("/stop/{device}")
async def stop_inventory(device: str):
    try:
        status, msg = validate_device(device=device)
        if not status:
            print("[ STOP ]", msg)
            raise HTTPException(status_code=422, detail=msg)

        print(f"STOP -> {device}")
        await devices.stop_inventory(device)
        return {"msg": msg}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": e})


@router.post("/clear/{device}")
async def clear_tags(device: str):
    print(f"CLEAR -> {device}")
    await devices.clear_tags(device)
    return {"msg": f"{device} clear tags"}

@router.post("/set_gpo/{device}/{gpo_pin}/{state}/{control}/{time}")
async def set_gpo(device: str, gpo_pin: int, state: bool, control: str, time: int = 1000):
    try:
        # 1. Validação do dispositivo
        try:
            status, msg = validate_device(device=device, need_connected=False)
            if not status:
                raise HTTPException(status_code=422, detail=msg)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{str(e)}")

        # 2. Monta os dados e executa o comando
        try:
            gpo_data = {
                "gpo_pin": gpo_pin,
                "state": state,
                "control": control,
                "time": time
            }

            result = await devices.set_gpo(device, gpo_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{str(e)}")

        # 3. Resposta final
        if result:
            print(f"SET_GPO -> {device} - {state}")
            return {"msg": f"GPO {device}, {state}"}
        else:
            print(f"{device} não possui GPO configurado")
            return JSONResponse(status_code=404, content={"msg": f"Dispositivo {device} não possui GPO"})

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": f"Erro interno inesperado: {str(e)}"})

