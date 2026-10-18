from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.country import country_service

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/", methods=["GET"])
def dashboard():
    edit_code = request.args.get("editar", "").strip()
    editing_country = country_service.get_by_code(edit_code) if edit_code else None

    countries = country_service.list_all()
    metrics = country_service.get_instrumentation()

    return render_template(
        "admin.html",
        countries=countries,
        editing_country=editing_country,
        metrics=metrics,
    )


@admin_bp.route("/paises/criar", methods=["POST"])
def create_country():
    code = request.form.get("code", "").strip()
    payload = {
        "country": request.form.get("country", ""),
        "region": request.form.get("region", ""),
        "provider": request.form.get("provider", ""),
        "tech": request.form.get("tech", ""),
        "lat": request.form.get("lat", 0.0),
        "lng": request.form.get("lng", 0.0),
    }

    try:
        created = country_service.create(code, payload)
        flash(f"País '{created['country']} ({created['code']})' cadastrado com sucesso na Tabela Hash!", "success")
    except (ValueError, KeyError) as err:
        flash(str(err), "error")

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/paises/<string:code>/atualizar", methods=["POST"])
def update_country(code: str):
    payload = {
        "country": request.form.get("country", ""),
        "region": request.form.get("region", ""),
        "provider": request.form.get("provider", ""),
        "tech": request.form.get("tech", ""),
        "lat": request.form.get("lat", 0.0),
        "lng": request.form.get("lng", 0.0),
    }

    try:
        updated = country_service.update(code, payload)
        flash(f"Dados de '{updated['country']} ({updated['code']})' atualizados com sucesso!", "success")
    except (ValueError, KeyError) as err:
        flash(str(err), "error")

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/paises/<string:code>/remover", methods=["POST"])
def delete_country(code: str):
    try:
        removed = country_service.delete(code)
        flash(f"País '{removed['country']} ({removed['code']})' removido da Tabela Hash e do JSON.", "success")
    except KeyError as err:
        flash(str(err), "error")

    return redirect(url_for("admin.dashboard"))
