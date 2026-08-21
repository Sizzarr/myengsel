from __future__ import annotations

import base64
import io
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from webapp.auth_store import AuthWeb

STATIC_DIR = Path(__file__).parent / "static"
app = FastAPI(title="myXL Web Paket", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class OTPRequest(BaseModel):
    number: str


class OTPSubmit(BaseModel):
    number: str
    otp: str


class AccountAction(BaseModel):
    number: int


class PackageAction(BaseModel):
    option_code: str


class PurchaseAction(BaseModel):
    option_code: str
    method: str
    wallet_number: str = ""


class UnsubscribeAction(BaseModel):
    quota_code: str
    product_subscription_type: str = ""
    product_domain: str = ""


class BookmarkRemove(BaseModel):
    family_code: str
    variant_name: str
    order: int
    is_enterprise: bool = False


class BookmarkAdd(BaseModel):
    family_code: str
    family_name: str
    variant_name: str
    option_name: str
    order: int = 0
    is_enterprise: bool = False


class FamilyLimit(BaseModel):
    family_member_id: str
    original_allocation: int
    new_allocation_mb: int


class FamilyRemove(BaseModel):
    family_member_id: str


class FamilyChange(BaseModel):
    parent_alias: str
    alias: str
    slot_id: int
    family_member_id: str
    msisdn: str


class CircleCreate(BaseModel):
    parent_name: str
    group_name: str
    member_msisdn: str
    member_name: str


class CircleInvite(BaseModel):
    msisdn: str
    name: str
    group_id: str
    parent_member_id: str


class CircleMemberAction(BaseModel):
    group_id: str
    member_id: str
    parent_member_id: str = ""
    is_last_member: bool = False


class RegistrationAction(BaseModel):
    msisdn: str
    nik: str
    kk: str


class ValidateMsisdnAction(BaseModel):
    msisdn: str


def api_error(exc: Exception) -> HTTPException:
    import traceback
    import sys
    print(f"[API_ERROR] {type(exc).__name__}: {exc}")
    traceback.print_exc()
    sys.stdout.flush()
    sys.stderr.flush()
    return HTTPException(status_code=400, detail=str(exc))


from fastapi import FastAPI, HTTPException, Request

def active_ctx(req: Request):
    try:
        num = req.headers.get("X-Number")
        rt = req.headers.get("X-Refresh-Token")
        sub_id = req.headers.get("X-Subscriber-Id", "")
        sub_type = req.headers.get("X-Subscription-Type", "")
        
        if not num or not num.isdigit() or not rt:
            raise HTTPException(status_code=401, detail="Belum login atau kredensial tidak lengkap.")
            
        user = AuthWeb.get_active(int(num), rt, sub_id, sub_type)
        if not user:
            raise HTTPException(status_code=401, detail="Sesi login tidak valid.")
        return user, AuthWeb.api_key, user.tokens
    except HTTPException:
        raise
    except Exception as exc:
        raise api_error(exc)


def fmt_date(ts: Any) -> str:
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%d %b %Y")
    except Exception:
        return "-"


@app.get("/api/cron/keepalive")
def cron_keepalive(req: Request):
    try:
        from sqlalchemy import text
        from webapp.db import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "message": "Database is awake."}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/auth/request-otp")
def request_otp(body: OTPRequest):
    number = body.number.strip()
    if not number.startswith("628") or not number.isdigit() or not 10 <= len(number) <= 14:
        raise HTTPException(status_code=422, detail="Nomor harus diawali 628 dan terdiri dari 10–14 digit.")
    try:
        from app.client.ciam import get_otp
        subscriber_id = get_otp(number)
        if not subscriber_id:
            raise RuntimeError("OTP gagal dikirim.")
        return {"ok": True, "subscriber_id": subscriber_id, "number": number}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/auth/submit-otp")
def submit_otp_route(body: OTPSubmit):
    if not body.otp.isdigit() or len(body.otp) != 6:
        raise HTTPException(status_code=422, detail="OTP harus 6 digit.")
    try:
        from app.client.ciam import submit_otp
        tokens = submit_otp(AuthWeb.api_key, "SMS", body.number, body.otp)
        if not tokens:
            raise RuntimeError("OTP salah atau sudah kedaluwarsa.")
        user = AuthWeb.add_login(int(body.number), tokens)
        return {
            "ok": True,
            "user": {
                "number": user.number,
                "subscriber_id": user.subscriber_id,
                "subscription_type": user.subscription_type,
            },
            "tokens": user.tokens
        }
    except Exception as exc:
        raise api_error(exc)




@app.get("/api/dashboard")
def dashboard(req: Request):
    user, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import get_balance, get_tiering_info, dashboard_segments

        balance = get_balance(api_key, tokens["id_token"]) or {}
        tiering = {}
        if user.subscription_type == "PREPAID":
            tiering = get_tiering_info(api_key, tokens) or {}

        notifications = []
        try:
            seg = dashboard_segments(api_key, tokens) or {}
            notifications = seg.get("data", {}).get("notification", {}).get("data", []) or []
        except Exception:
            pass

        return {
            "user": {
                "number": user.number,
                "subscriber_id": user.subscriber_id,
                "subscription_type": user.subscription_type,
            },
            "balance": {
                "remaining": balance.get("remaining", 0),
                "expired_at": balance.get("expired_at", 0),
                "expired_label": fmt_date(balance.get("expired_at")),
            },
            "points": {
                "current": tiering.get("current_point", 0),
                "tier": tiering.get("tier", "N/A"),
            },
            "notification_count": len(notifications),
            "unread_count": sum(1 for n in notifications if not n.get("is_read", False)),
        }
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/packages")
def my_packages(req: Request):
    user, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import send_api_request
        res = send_api_request(
            api_key,
            "api/v8/packages/quota-details",
            {"is_enterprise": False, "lang": "en", "family_member_id": ""},
            tokens["id_token"],
            "POST",
        )
        if not isinstance(res, dict) or res.get("status") != "SUCCESS":
            raise RuntimeError("Gagal mengambil paket aktif.")
        return {"packages": res.get("data", {}).get("quotas", [])}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/packages/unsubscribe")
def unsubscribe_package(req: Request, body: UnsubscribeAction):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import unsubscribe
        ok = unsubscribe(api_key, tokens, body.quota_code, body.product_domain, body.product_subscription_type)
        return {"ok": bool(ok)}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/store/segments")
def store_segments(req: Request):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.store.segments import get_segments
        res = get_segments(api_key, tokens, False) or {}
        return res
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/store/families")
def store_families(req: Request):
    user, api_key, tokens = active_ctx(req)
    try:
        from app.client.store.search import get_family_list
        return get_family_list(api_key, tokens, user.subscription_type or "PREPAID", False) or {}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/store/packages")
def store_packages(req: Request):
    user, api_key, tokens = active_ctx(req)
    try:
        from app.client.store.search import get_store_packages
        return get_store_packages(api_key, tokens, user.subscription_type or "PREPAID", False) or {}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/family/{family_code}")
def family_detail(req: Request, family_code: str):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import get_family
        data = get_family(api_key, tokens, family_code, False, None)
        if not data:
            raise RuntimeError("Family paket tidak ditemukan.")
        return {"data": data}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/package/{option_code}")
def package_detail(req: Request, option_code: str):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import get_package, get_addons
        package = get_package(api_key, tokens, option_code)
        if not package:
            raise RuntimeError("Detail paket tidak ditemukan.")
        addons = get_addons(api_key, tokens, option_code) or {}
        return {"package": package, "addons": addons}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/purchase")
def purchase(req: Request, body: PurchaseAction):
    _, api_key, tokens = active_ctx(req)
    method = body.method.upper().strip()
    if method not in {"BALANCE", "QRIS", "DANA", "SHOPEEPAY", "GOPAY", "OVO"}:
        raise HTTPException(status_code=422, detail="Metode pembayaran tidak didukung.")
    try:
        from app.client.engsel import get_package
        from app.client.purchase.balance import settlement_balance
        from app.client.purchase.ewallet import settlement_multipayment
        from app.client.purchase.qris import settlement_qris, get_qris_code

        pkg = get_package(api_key, tokens, body.option_code)
        if not pkg:
            raise RuntimeError("Paket tidak ditemukan.")
        option = pkg.get("package_option", {})
        family = pkg.get("package_family", {})
        variant = pkg.get("package_detail_variant", {}) or {}
        price = int(option.get("price", 0) or 0)
        item = {
            "item_code": body.option_code,
            "product_type": "",
            "item_price": price,
            "item_name": f"{variant.get('name', '')} {option.get('name', '')}".strip(),
            "tax": 0,
            "token_confirmation": pkg.get("token_confirmation", ""),
        }
        payment_for = family.get("payment_for") or "BUY_PACKAGE"

        if method == "BALANCE":
            res = settlement_balance(api_key, tokens, [item], payment_for, False, overwrite_amount=price)
            return {"ok": isinstance(res, dict) and res.get("status") == "SUCCESS", "result": res}

        if method == "QRIS":
            trx = settlement_qris(api_key, tokens, [item], payment_for, False, overwrite_amount=price)
            if not trx:
                raise RuntimeError("Gagal membuat transaksi QRIS.")
            qris_data = get_qris_code(api_key, tokens, trx)
            if not qris_data:
                raise RuntimeError("QRIS tidak tersedia.")

            import qrcode
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(qris_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            png_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return {"ok": True, "transaction_id": trx, "qris": qris_data, "qr_png": f"data:image/png;base64,{png_b64}"}

        if method in {"DANA", "OVO"}:
            n = body.wallet_number.strip()
            if not (n.startswith("08") and n.isdigit() and 10 <= len(n) <= 13):
                raise HTTPException(status_code=422, detail=f"Nomor {method} tidak valid.")
        res = settlement_multipayment(
            api_key, tokens, [item], body.wallet_number.strip(), method, payment_for,
            False, overwrite_amount=price,
        )
        return {"ok": isinstance(res, dict) and res.get("status") == "SUCCESS", "result": res}
    except HTTPException:
        raise
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/transactions")
def transactions(req: Request):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import get_transaction_history
        data = get_transaction_history(api_key, tokens) or {}
        return {"transactions": data.get("list", []) if isinstance(data, dict) else []}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/rewards")
def rewards(req: Request):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.store.redeemables import get_redeemables
        return get_redeemables(api_key, tokens, False) or {}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/notifications")
def notifications(req: Request):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import dashboard_segments
        res = dashboard_segments(api_key, tokens) or {}
        items = res.get("data", {}).get("notification", {}).get("data", []) or []
        return {"notifications": items}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/notifications/read-all")
def notifications_read_all(req: Request):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.engsel import dashboard_segments, get_notification_detail
        res = dashboard_segments(api_key, tokens) or {}
        items = res.get("data", {}).get("notification", {}).get("data", []) or []
        count = 0
        for item in items:
            if item.get("is_read", False):
                continue
            nid = item.get("notification_id")
            if nid:
                get_notification_detail(api_key, tokens, nid)
                count += 1
        return {"ok": True, "read": count}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/family-plan")
def family_plan(req: Request):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.famplan import get_family_data
        return get_family_data(api_key, tokens) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/family-plan/limit")
def family_plan_limit(req: Request, body: FamilyLimit):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.famplan import set_quota_limit
        return set_quota_limit(api_key, tokens, body.original_allocation, body.new_allocation_mb * 1024 * 1024, body.family_member_id) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/family-plan/remove")
def family_plan_remove(req: Request, body: FamilyRemove):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.famplan import remove_member
        return remove_member(api_key, tokens, body.family_member_id) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/family-plan/change")
def family_plan_change(req: Request, body: FamilyChange):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.famplan import validate_msisdn, change_member
        valid = validate_msisdn(api_key, tokens, body.msisdn) or {}
        if str(valid.get("status", "")).upper() != "SUCCESS":
            raise RuntimeError("MSISDN gagal divalidasi.")
        role = valid.get("data", {}).get("family_plan_role", "")
        if role and role != "NO_ROLE":
            raise RuntimeError(f"Nomor sudah berada dalam Family Plan dengan role {role}.")
        return change_member(api_key, tokens, body.parent_alias, body.alias, body.slot_id, body.family_member_id, body.msisdn) or {}
    except Exception as exc:
        raise api_error(exc)


@app.get("/api/circle")
def circle(req: Request):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.circle import get_group_data, get_group_members, spending_tracker, get_bonus_data
        from app.client.encrypt import decrypt_circle_msisdn
        group_res = get_group_data(api_key, tokens) or {}
        if group_res.get("status") != "SUCCESS":
            return group_res
        group = group_res.get("data", {}) or {}
        group_id = group.get("group_id", "")
        if not group_id:
            return {"status": "SUCCESS", "data": {"group": group, "members": [], "package": {}, "spending": {}, "bonuses": []}}
        member_res = get_group_members(api_key, tokens, group_id) or {}
        member_data = member_res.get("data", {}) or {}
        members = member_data.get("members", []) or []
        parent_subs_id = ""
        parent_member_id = ""
        cleaned = []
        for member in members:
            item = dict(member)
            try:
                item["plain_msisdn"] = decrypt_circle_msisdn(api_key, item.get("msisdn", "")) if item.get("msisdn") else ""
            except Exception:
                item["plain_msisdn"] = ""
            if item.get("member_role") == "PARENT":
                parent_subs_id = item.get("subscriber_number", "")
                parent_member_id = item.get("member_id", "")
            cleaned.append(item)
        spending = {}
        bonuses = []
        if parent_subs_id:
            spend_res = spending_tracker(api_key, tokens, parent_subs_id, group_id) or {}
            spending = spend_res.get("data", {}) or {}
            bonus_res = get_bonus_data(api_key, tokens, parent_subs_id, group_id) or {}
            bonuses = bonus_res.get("data", {}).get("bonuses", []) or []
        return {"status": "SUCCESS", "data": {
            "group": group, "members": cleaned, "package": member_data.get("package", {}) or {},
            "spending": spending, "bonuses": bonuses, "parent_member_id": parent_member_id
        }}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/circle/create")
def circle_create(req: Request, body: CircleCreate):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.circle import create_circle
        return create_circle(api_key, tokens, body.parent_name, body.group_name, body.member_msisdn, body.member_name) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/circle/invite")
def circle_invite(req: Request, body: CircleInvite):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.circle import validate_circle_member, invite_circle_member
        valid = validate_circle_member(api_key, tokens, body.msisdn) or {}
        if valid.get("status") != "SUCCESS":
            raise RuntimeError("Nomor tidak dapat divalidasi untuk Circle.")
        return invite_circle_member(api_key, tokens, body.msisdn, body.name, body.group_id, body.parent_member_id) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/circle/remove")
def circle_remove(req: Request, body: CircleMemberAction):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.circle import remove_circle_member
        return remove_circle_member(api_key, tokens, body.member_id, body.group_id, body.parent_member_id, body.is_last_member) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/circle/accept")
def circle_accept(req: Request, body: CircleMemberAction):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.circle import accept_circle_invitation
        return accept_circle_invitation(api_key, tokens, body.group_id, body.member_id) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/tools/register")
def register_number(req: Request, body: RegistrationAction):
    try:
        from app.client.registration import dukcapil
        return dukcapil(AuthWeb.api_key, body.msisdn, body.kk, body.nik) or {}
    except Exception as exc:
        raise api_error(exc)


@app.post("/api/tools/validate-msisdn")
def validate_msisdn_route(req: Request, body: ValidateMsisdnAction):
    _, api_key, tokens = active_ctx(req)
    try:
        from app.client.famplan import validate_msisdn
        return validate_msisdn(api_key, tokens, body.msisdn) or {}
    except Exception as exc:
        raise api_error(exc)