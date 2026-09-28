import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(
    page_title="Quản lý phòng khách sạn",
    page_icon="🏨",
    layout="wide"
)

# =========================
# DỮ LIỆU KHỞI TẠO
# =========================
if "rooms" not in st.session_state:
    room_types = {
        "101": ("Standard", 500000),
        "102": ("Standard", 500000),
        "103": ("Standard", 500000),
        "104": ("Standard", 500000),
        "105": ("Standard", 500000),
        "201": ("Deluxe", 800000),
        "202": ("Deluxe", 800000),
        "203": ("Deluxe", 800000),
        "204": ("Deluxe", 800000),
        "205": ("Deluxe", 800000),
        "301": ("Superior", 1000000),
        "302": ("Superior", 1000000),
        "303": ("Superior", 1000000),
        "304": ("Superior", 1000000),
        "305": ("Superior", 1000000),
        "401": ("Suite", 1500000),
        "402": ("Suite", 1500000),
        "403": ("Suite", 1500000),
        "404": ("Suite", 1500000),
        "405": ("Suite", 1500000),
        "501": ("Family", 1800000),
        "502": ("Family", 1800000),
        "503": ("Family", 1800000),
        "504": ("Family", 1800000),
        "505": ("Family", 1800000),
        "601": ("VIP", 2500000),
        "602": ("VIP", 2500000),
        "603": ("VIP", 2500000),
        "604": ("VIP", 2500000),
        "605": ("VIP", 2500000),
    }

    st.session_state.rooms = pd.DataFrame([
        {
            "Phòng": room,
            "Loại phòng": info[0],
            "Giá/đêm": info[1],
            "Trạng thái": "Trống",
            "Khách": "",
            "Ngày nhận": None,
            "Ngày trả": None,
        }
        for room, info in room_types.items()
    ])

if "bookings" not in st.session_state:
    st.session_state.bookings = pd.DataFrame(
        columns=[
            "Mã đặt phòng", "Phòng", "Khách hàng", "SĐT",
            "Ngày nhận", "Ngày trả", "Số đêm", "Tổng tiền", "Trạng thái"
        ]
    )

# =========================
# HÀM TIỆN ÍCH
# =========================
def money(value):
    return f"{int(value):,} VNĐ".replace(",", ".")

def status_color(status):
    return {
        "Trống": "🟢",
        "Đã đặt": "🟡",
        "Đang ở": "🔴",
        "Bảo trì": "🔧",
    }.get(status, "⚪")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🏨 HOTEL MANAGER")
menu = st.sidebar.radio(
    "Chức năng",
    [
        "📊 Tổng quan",
        "🛏️ Quản lý phòng",
        "📅 Đặt phòng",
        "👤 Nhận / trả phòng",
        "💰 Doanh thu",
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Ứng dụng quản lý phòng khách sạn bằng Streamlit")

# =========================
# TỔNG QUAN
# =========================
if menu == "📊 Tổng quan":
    st.title("🏨 HỆ THỐNG QUẢN LÝ KHÁCH SẠN")

    rooms = st.session_state.roomsbookings = st.session_state.bookings

    total = len(rooms)
    available = len(rooms[rooms["Trạng thái"] == "Trống"])
    reserved = len(rooms[rooms["Trạng thái"] == "Đã đặt"])
    occupied = len(rooms[rooms["Trạng thái"] == "Đang ở"])
    maintenance = len(rooms[rooms["Trạng thái"] == "Bảo trì"])

    revenue = bookings["Tổng tiền"].sum() if not bookings.empty else 0
    occupancy = ((occupied + reserved) / total * 100) if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tổng phòng", total)
    c2.metric("🟢 Phòng trống", available)
    c3.metric("🟡 Đã đặt", reserved)
    c4.metric("🔴 Đang ở", occupied)
    c5.metric("🔧 Bảo trì", maintenance)

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Công suất phòng")
        st.metric("Tỷ lệ sử dụng / đặt", f"{occupancy:.1f}%")

    with c2:
        st.subheader("💰 Doanh thu")
        st.metric("Tổng doanh thu", money(revenue))

    st.subheader("🛏️ Tình trạng phòng")

    display = rooms[["Phòng", "Loại phòng", "Giá/đêm", "Trạng thái", "Khách"]].copy()
    display["Trạng thái"] = display["Trạng thái"].apply(
        lambda x: f"{status_color(x)} {x}"
    )
    st.dataframe(display, use_container_width=True, hide_index=True)

# =========================
# QUẢN LÝ PHÒNG
# =========================
elif menu == "🛏️ Quản lý phòng":
    st.title("🛏️ QUẢN LÝ PHÒNG")

    rooms = st.session_state.rooms

    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔎 Tìm số phòng")
    with col2:
        filter_status = st.selectbox(
            "Lọc trạng thái",
            ["Tất cả", "Trống", "Đã đặt", "Đang ở", "Bảo trì"]
        )

    filtered = rooms.copy()

    if search:
        filtered = filtered[
            filtered["Phòng"].astype(str).str.contains(search, case=False)
        ]

    if filter_status != "Tất cả":
        filtered = filtered[filtered["Trạng thái"] == filter_status]

    st.dataframe(
        filtered[["Phòng", "Loại phòng", "Giá/đêm", "Trạng thái", "Khách"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("⚙️ Cập nhật trạng thái phòng")

    with st.form("update_room"):
        room = st.selectbox("Chọn phòng", rooms["Phòng"].tolist())
        new_status = st.selectbox(
            "Trạng thái mới",
            ["Trống", "Đã đặt", "Đang ở", "Bảo trì"]
        )
        customer = st.text_input("Tên khách (nếu có)")
        submit = st.form_submit_button("💾 Cập nhật")

        if submit:
            idx = st.session_state.rooms.index[
                st.session_state.rooms["Phòng"] == room
            ][0]

            st.session_state.rooms.at[idx, "Trạng thái"] = new_statusst.session_state.rooms.at[idx, "Khách"] = customer
            st.success(f"Đã cập nhật phòng {room}.")

# =========================
# ĐẶT PHÒNG
# =========================
elif menu == "📅 Đặt phòng":
    st.title("📅 ĐẶT PHÒNG")

    rooms = st.session_state.rooms
    available_rooms = rooms[rooms["Trạng thái"] == "Trống"]

    if available_rooms.empty:
        st.warning("Hiện không còn phòng trống.")
    else:
        with st.form("booking_form"):
            col1, col2 = st.columns(2)

            with col1:
                customer = st.text_input("👤 Họ tên khách *")
                phone = st.text_input("📱 Số điện thoại")
                room = st.selectbox(
                    "🛏️ Chọn phòng *",
                    available_rooms["Phòng"].tolist()
                )

            with col2:
                checkin = st.date_input("📅 Ngày nhận", value=date.today())
                checkout = st.date_input(
                    "📅 Ngày trả",
                    value=date.today()
                )

            submit = st.form_submit_button("✅ Xác nhận đặt phòng")

            if submit:
                if not customer.strip():
                    st.error("Vui lòng nhập tên khách.")
                elif checkout <= checkin:
                    st.error("Ngày trả phải sau ngày nhận.")
                else:
                    room_data = rooms[rooms["Phòng"] == room].iloc[0]
                    nights = (checkout - checkin).days
                    total_price = nights * room_data["Giá/đêm"]

                    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    new_booking = pd.DataFrame([{
                        "Mã đặt phòng": booking_id,
                        "Phòng": room,
                        "Khách hàng": customer,
                        "SĐT": phone,
                        "Ngày nhận": checkin,
                        "Ngày trả": checkout,
                        "Số đêm": nights,
                        "Tổng tiền": total_price,
                        "Trạng thái": "Đã đặt"
                    }])

                    st.session_state.bookings = pd.concat(
                        [st.session_state.bookings, new_booking],
                        ignore_index=True
                    )

                    idx = st.session_state.rooms.index[
                        st.session_state.rooms["Phòng"] == room
                    ][0]

                    st.session_state.rooms.at[idx, "Trạng thái"] = "Đã đặt"
                    st.session_state.rooms.at[idx, "Khách"] = customer
                    st.session_state.rooms.at[idx, "Ngày nhận"] = checkin
                    st.session_state.rooms.at[idx, "Ngày trả"] = checkout

                    st.success(
                        f"Đặt phòng thành công! Tổng tiền: {money(total_price)}")

    if not st.session_state.bookings.empty:
        st.markdown("---")
        st.subheader("📋 Danh sách đặt phòng")

        show = st.session_state.bookings.copy()
        show["Tổng tiền"] = show["Tổng tiền"].apply(money)
        st.dataframe(show, use_container_width=True, hide_index=True)

# =========================
# NHẬN / TRẢ PHÒNG
# =========================
elif menu == "👤 Nhận / trả phòng":
    st.title("👤 NHẬN / TRẢ PHÒNG")

    rooms = st.session_state.rooms

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔑 Nhận phòng")
        checked_in = rooms[rooms["Trạng thái"] == "Đã đặt"]

        if checked_in.empty:
            st.info("Không có phòng đang chờ nhận.")
        else:
            selected = st.selectbox(
                "Chọn phòng",
                checked_in["Phòng"].tolist(),
                key="checkin_room"
            )

            if st.button("🔑 Xác nhận nhận phòng"):
                idx = st.session_state.rooms.index[
                    st.session_state.rooms["Phòng"] == selected
                ][0]

                st.session_state.rooms.at[idx, "Trạng thái"] = "Đang ở"

                booking_idx = st.session_state.bookings.index[
                    st.session_state.bookings["Phòng"] == selected
                ]

                if len(booking_idx):
                    st.session_state.bookings.loc[
                        booking_idx[-1], "Trạng thái"
                    ] = "Đang ở"

                st.success(f"Phòng {selected} đã nhận khách.")

    with col2:
