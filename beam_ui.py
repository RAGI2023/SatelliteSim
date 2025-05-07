import streamlit as st
import pandas as pd
import plotly.express as px
from BackEnd.beam_control import BeamControlSystem

st.set_page_config(page_title="Beam 控制系统", layout="wide")

if "bcs" not in st.session_state:
    st.session_state.bcs = BeamControlSystem(
        n_beams=10,
        beam_radius=500,
        max_users_per_beam=5,
        freq_list=[800, 1800, 2600]
    )
    st.success("Beam 控制系统已初始化")

bcs = st.session_state.bcs

st.sidebar.header("用户操作")

# 添加用户
with st.sidebar.expander("➕ 添加用户"):
    new_user_id = st.number_input("用户 ID", min_value=0, step=1)
    new_lat = st.number_input("纬度 [-60, 60]", min_value=-60.0, max_value=60.0, step=0.1)
    new_lon = st.number_input("经度 [-180, 180]", min_value=-180.0, max_value=180.0, step=0.1)
    if st.button("添加用户"):
        try:
            bcs.add_user(new_user_id, (new_lat, new_lon))
            bcs.assign_users_to_beams()
            st.success(f"✅ 用户 {new_user_id} 添加成功")
        except Exception as e:
            st.error(str(e))

# 移动用户
with st.sidebar.expander("🚶‍♂️ 移动用户"):
    move_user_id = st.number_input("用户 ID", min_value=0, step=1, key="move_user")
    move_lat = st.number_input("新纬度", min_value=-60.0, max_value=60.0, step=0.1, key="move_lat")
    move_lon = st.number_input("新经度", min_value=-180.0, max_value=180.0, step=0.1, key="move_lon")
    if st.button("更新位置"):
        try:
            bcs.dynamic_beam_switch(move_user_id, (move_lat, move_lon))
            st.success(f"✅ 用户 {move_user_id} 位置已更新")
        except Exception as e:
            st.error(str(e))

# 删除用户
with st.sidebar.expander("❌ 删除用户"):
    del_user_id = st.number_input("用户 ID", min_value=0, step=1, key="del_user")
    if st.button("删除用户"):
        try:
            bcs.remove_user(del_user_id)
            st.success(f"✅ 用户 {del_user_id} 已删除")
        except Exception as e:
            st.error(str(e))

# Beam 功率调整
with st.sidebar.expander("🔋 调整Beam功率"):
    beam_id = st.number_input("Beam ID", min_value=0, max_value=bcs.n_beams-1, step=1)
    new_power = st.slider("新功率", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    if st.button("设置功率"):
        try:
            bcs.set_beam_power(beam_id, new_power)
            st.success(f"Beam {beam_id} 功率已设为 {new_power}")
        except Exception as e:
            st.error(str(e))

# Beam 中心调整
with st.sidebar.expander("🎯 调整Beam中心"):
    beam_id2 = st.number_input("Beam ID ", min_value=0, max_value=bcs.n_beams-1, step=1, key="center_beam")
    center_x = st.number_input("中心纬度", min_value=-90.0, max_value=90.0, step=0.1, key="center_x")
    center_y = st.number_input("中心经度", min_value=-180.0, max_value=180.0, step=0.1, key="center_y")
    if st.button("设置中心"):
        try:
            bcs.set_beam_center(beam_id2, (center_x, center_y))
            bcs.assign_users_to_beams()
            st.success(f"Beam {beam_id2} 中心已设为 ({center_x},{center_y})")
        except Exception as e:
            st.error(str(e))

# 自动分配
if st.sidebar.button("🔄 自动分配用户到Beam"):
    bcs.assign_users_to_beams()
    st.sidebar.success("已自动分配")

# 自动功率控制
if st.sidebar.button("⚡ 启动自动功率控制"):
    bcs.auto_power_control()
    st.sidebar.success("自动功率控制已应用")

# 频率复用分析
if st.sidebar.button("🔁 频率复用分析"):
    reuse = bcs.frequency_reuse()
    if not reuse:
        st.sidebar.success("无频率复用冲突")
    else:
        st.sidebar.error(f"发现 {len(reuse)} 个冲突：")
        for r in reuse:
            st.sidebar.write(f"Beam {r[0]} 与 Beam {r[1]} 在频率 {r[2]} MHz 距离 {r[3]} km")

st.title("📡 Beam 控制与可视化系统")

vis = bcs.visualize()
beams = vis["beams"]
users = vis["users"]

st.subheader("🌍 实时地图")
beam_df = pd.DataFrame(beams)
user_df = pd.DataFrame(users)

if not beam_df.empty:
    beam_df = beam_df[beam_df["center"].apply(lambda x: isinstance(x, (list, tuple)) and len(x) == 2)]
    beam_df["lat"] = beam_df["center"].apply(lambda x: x[0])
    beam_df["lon"] = beam_df["center"].apply(lambda x: x[1])
else:
    beam_df["lat"] = []
    beam_df["lon"] = []

if not user_df.empty:
    user_df = user_df[user_df["pos"].apply(lambda x: isinstance(x, (list, tuple)) and len(x) == 2)]
    user_df["lat"] = user_df["pos"].apply(lambda x: x[0])
    user_df["lon"] = user_df["pos"].apply(lambda x: x[1])
else:
    user_df["lat"] = []
    user_df["lon"] = []

fig = px.scatter_mapbox(
    beam_df,
    lat="lat",
    lon="lon",
    hover_name="beam_id",
    hover_data=["power", "user_count", "freq"],
    size=[30] * len(beam_df) if len(beam_df) > 0 else None,
    color_discrete_sequence=["blue"],
    zoom=1,
    height=500
)
if not user_df.empty:
    fig.add_scattermapbox(
        lat=user_df["lat"],
        lon=user_df["lon"],
        mode="markers",
        marker=dict(size=9, color="red"),
        text=["用户 " + str(uid) for uid in user_df["user_id"]],
        name="用户"
    )
fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 系统状态表格")
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Beam 状态")
    if not beam_df.empty and all(col in beam_df.columns for col in ["beam_id", "power", "freq", "user_count"]):
        st.dataframe(beam_df[["beam_id", "power", "freq", "user_count"]])
    else:
        st.info("暂无 Beam 数据")
with col2:
    st.markdown("### 用户状态")
    if not user_df.empty and all(col in user_df.columns for col in ["user_id", "connected_beam"]):
        st.dataframe(user_df[["user_id", "connected_beam"]])
    else:
        st.info("暂无用户数据")

with st.expander("🚨 干扰检测"):
    interference = bcs.interference_check()
    if not interference:
        st.success("✅ 无干扰波束")
    else:
        st.error(f"⚠️ 发现 {len(interference)} 个干扰：")
        for i in interference:
            st.write(f"Beam {i[0]} 与 Beam {i[1]} 在频率 {i[2]} MHz 发生干扰")
