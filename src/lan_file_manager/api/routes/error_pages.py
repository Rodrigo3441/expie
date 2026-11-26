from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/404")
def not_found_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "404.html",
        status_code=404
    )

@router.get("/403")
def forbidden_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "403.html",
        status_code=403
    )