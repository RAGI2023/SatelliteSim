import re
class Satellite:
    def __init__(self, index, name, r, angle, angular_speed):
        self.index = int(index)
        self.name = name
        self.r = float(r)
        self.angle = float(angle)
        self.angular_speed = float(angular_speed)
    def __repr__(self):
        return f"Satellite {self.index}: {self.name}, angle={self.angle}"

#输入的messages用 , 和 \n 将每个卫星的信息分隔开
def plan_satellite_path(messages):
    #定义正则表达式
    pattern = r"Satellite (\d+): (.*?), Position: \((\d+), ([\d\.]+), ([\d\.]+)\)"
    satellites = []
    #正则表达式处理提取卫星信息
    for msg in messages:
        match = re.match(pattern, msg)
        if match:
            index, name, r, angle, angular_speed = match.groups()
            satellites.append(Satellite(index, name, r, angle, angular_speed))
        else:
            raise ValueError(f"格式出错: {msg}")
    #按照角度排序
    satellites.sort(key=lambda s: s.angle)

    return " ".join(str(s.index) for s in satellites)
