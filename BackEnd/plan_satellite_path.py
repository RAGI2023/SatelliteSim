def plan_satellite_path(satellites, start_index, end_index):
    """
    计算从起始卫星到目标卫星的最优转发路径，自动选择顺时针或逆时针方向，
    以最小化路径中任意一跳的最大角度变化。

    所有卫星按角度进行排序，然后分别构建顺时针和逆时针路径，
    比较它们在路径中的最大跳跃角度，选择跳跃最平滑的路径。

    Args:
        satellites (List[dict]): 卫星列表，每个卫星为一个字典，至少包含：
            - 'index': 卫星索引
            - 'angle': 当前角度（单位：度，范围 0~360）
        start_index (int): 起始卫星的 index
        end_index (int): 目标卫星的 index

    Returns:
        List[int]: 最优路径上经过的卫星索引列表（包含起点和终点）
    """   
    # 按角度排序
    sorted_sats = sorted(satellites, key=lambda s: s['angle'])
    index_ring = [sat['index'] for sat in sorted_sats]
    angle_map = {sat['index']: sat['angle'] for sat in satellites}

    def build_path(start, end, clockwise=True):
        start_pos = index_ring.index(start)
        end_pos = index_ring.index(end)
        path = []

        if clockwise:
            if end_pos < start_pos:
                end_pos += len(index_ring)
            path = [index_ring[i % len(index_ring)] for i in range(start_pos, end_pos + 1)]
        else:
            if end_pos > start_pos:
                start_pos += len(index_ring)
            path = [index_ring[i % len(index_ring)] for i in range(start_pos, end_pos - 1, -1)]
        return path

    def max_jump_angle(path):
        return max(
            (angle_map[path[i+1]] - angle_map[path[i]]) % 360
            for i in range(len(path) - 1)
        )

    # 构造两种路径
    cw_path = build_path(start_index, end_index, clockwise=True)
    ccw_path = build_path(start_index, end_index, clockwise=False)

    # 计算每种路径的最大跳跃角度
    cw_max = max_jump_angle(cw_path)
    ccw_max = max_jump_angle(ccw_path)

    # 选择更平滑的路径
    if cw_max <= ccw_max:
        print(f"Using clockwise path (max jump {cw_max}°): {cw_path}")
        return cw_path
    else:
        print(f"Using counter-clockwise path (max jump {ccw_max}°): {ccw_path}")
        return ccw_path
