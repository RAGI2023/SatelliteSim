## 数据链路规划 API 文档

### 接口信息
- **IP 地址**：`127.0.0.1`  
- **端口**：`12345`

---

### 发送信息格式（客户端 → 服务端）

发送内容为一条字符串，描述单颗卫星的基本信息：

```python
message = f"Satellite {sat.index}: {sat.name}, Position: ({sat.r}, {sat.angle:.2f}, {1000.0 / self.opengl_widget.update_delta_t * sat.delta_deg:.2f})"
```

#### 字段说明：

| 字段                                                         | 含义                 |
| ------------------------------------------------------------ | -------------------- |
| `sat.index`                                                  | 卫星编号（唯一标识） |
| `sat.name`                                                   | 卫星名称             |
| `sat.r`                                                      | 公转半径             |
| `sat.angle`                                                  | 当前角度，单位：度   |
| `1000.0 / self.opengl_widget.update_delta_t * sat.delta_deg` | 每秒公转的度数       |

**最终格式示例：**
```
Satellite 3: SAT-Alpha, Position: (12000, 45.23, 5.76)
```

---

### 接收信息格式（服务端 → 客户端）

接收内容为一个字符串，包含推荐的链路连接顺序：

```text
"{sat1} {sat2} {sat3} {sat4} ..."
```

#### 要求：
- 每个 `sat` 为一个卫星编号（即 `sat.index`）
- 卫星数量不固定
- 数字之间用 **空格** 分隔

**示例：**
```
3 1 4 2
```

表示链路连接顺序为：卫星 3 → 1 → 4 → 2

