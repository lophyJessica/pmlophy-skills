# Tailwind → Ant Design 迁移踩坑记录 (2026-07-29)

## fork-erp 全量迁移实战

### ProTable 模式
```tsx
// ✅ 用 dataSource(先查Dexie再传入)
<ProTable columns={columns} dataSource={data} rowKey="id" />

// ❌ 不用 request(反重力容易写出死循环)
```

### 表单模式  
```tsx
// ✅ antd 原生 Form(反重力支持)
<Form layout="vertical" onFinish={handleSave}>
  <Row gutter={16}>
    <Col span={12}>
      <Form.Item name="code" label="编码" rules={[{required:true}]}>
        <Input disabled={isEdit} />
      </Form.Item>
    </Col>
  </Row>
</Form>

// ❌ ProForm子组件(反重力不支持,三次尝试均失败)
<ProFormText name="code" label="编码" />  // 不会生成
<ProFormSelect name="type" label="类型" />  // 不会生成
```

### 常见问题
1. **表单居中**: 删除 `max-w-2xl mx-auto` 等居中容器
2. **重复路由树**: 梭哈后 bundle 中 basename 出现 N 次,需手动删重复
3. **JS体积**: antd 全家桶从 1.2MB → 6MB
4. **ProForm 子组件**: 反重力/Gemini 不支持 ProFormText/ProFormSelect/ProFormDigit,必须用 antd 原生 Form.Item
