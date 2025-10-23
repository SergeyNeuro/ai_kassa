import asyncio
import logging
from typing import Any, Union, List, Optional
from datetime import datetime
import os
from PIL import Image
import io

from fastapi import APIRouter, UploadFile, File, Depends, Request
from fastapi.responses import JSONResponse

from servises.iiko import IikoAPI
from servises.auth_service import get_token_by_headers, AuthObj



logger = logging.getLogger(f"app.{__name__}")

router = APIRouter(prefix="/iiko", tags=['iiko'])


@router.get('/organizations')
async def get_organizations(
        menu_id: int,
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
):
    """Извлекаем из системы IIKO данные всех организаций"""

    # проверяем токен на валидность
    try:
        logger.info(f"Пришел запрос на извлечение всех организаций IIKO")

        auth_data =  await auth_obj.check_authenticate(token=token, api="predict")
        if not auth_data:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})
        if auth_data.role != 0:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})

        # прогоняем дальнейшую логику
        organizations_data = await IikoAPI(menu_id=menu_id).get_organizations()

        if organizations_data:
            return JSONResponse(status_code=200, content={"success": True, "data": organizations_data})
        else:
            return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})

    except Exception as _ex:
        logger.error(f"Ошибка извлечении организаций IIKO: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})


@router.get('/menu')
async def get_menu(
        menu_id: int,
        organization_id: str,
        iiko_menu_id: Optional[str] = None,
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
):
    """Извлекаем из системы IIKO данные по всем меню"""

    # проверяем токен на валидность
    try:
        logger.info(f"Пришел запрос на извлечение меню iiko, menu_id: {menu_id}, "
                    f"organization_id: {organization_id}, iiko_menu_id: {iiko_menu_id}")

        auth_data =  await auth_obj.check_authenticate(token=token, api="predict")
        if not auth_data:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})
        if auth_data.role != 0:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})

        # прогоняем дальнейшую логику
        if not iiko_menu_id:
            menu_data = await IikoAPI(menu_id=menu_id).get_menu(organization_id=organization_id)
        else:
            menu_data = await IikoAPI(menu_id=menu_id).get_menu_data(organization_id=organization_id, menu_id=iiko_menu_id)

        if menu_data:
            return JSONResponse(status_code=200, content={"success": True, "data": menu_data})
        else:
            return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})

    except Exception as _ex:
        logger.error(f"Ошибка извлечении menu IIKO: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})


@router.get('/terminals')
async def get_terminals(
        menu_id: int,
        organization_id: str,
        group_id: Optional[str] = None,
        token: Union[str, None] = Depends(get_token_by_headers),
        auth_obj=Depends(AuthObj),
):
    """Извлекаем из системы IIKO данные об терминалах"""

    # проверяем токен на валидность
    try:
        logger.info(f"Пришел запрос на извлечение терминалов iiko, menu_id: {menu_id}, "
                    f"organization_id: {organization_id}, group_id: {group_id}")

        auth_data =  await auth_obj.check_authenticate(token=token, api="predict")
        if not auth_data:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})
        if auth_data.role != 0:
            return JSONResponse(status_code=403, content={"success": False, "info": "authentication error"})

        # прогоняем дальнейшую логику
        if not group_id:
            terminals_data = await IikoAPI(menu_id=menu_id).get_terminals_groups(organization_id=organization_id)
        else:
            terminals_data = await IikoAPI(menu_id=menu_id).get_terminals(organization_id=organization_id, group_id=group_id)

        if terminals_data:
            return JSONResponse(status_code=200, content={"success": True, "data": terminals_data})
        else:
            return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})

    except Exception as _ex:
        logger.error(f"Ошибка извлечении menu IIKO: {_ex}")
        return JSONResponse(status_code=400, content={"success": False, "info": "indefinite error"})