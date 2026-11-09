// ProForm 独立路由表单页模板——反重力不会写 ProForm 子组件时,复制此模板改字段名。
import { ProForm, ProFormText, ProFormSelect, ProFormDigit, ProFormTextArea } from '@ant-design/pro-components'
import { useNavigate, useParams } from 'react-router-dom'
import { message } from 'antd'

interface FormProps {
  // 如需传入编辑数据: initialValues
}

export default function EntityForm({ }: FormProps) {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEdit = !!id

  const handleSubmit = async (values: any) => {
    // TODO: 保存到 Dexie 或 mock 数据
    console.log('保存数据:', values)
    message.success(isEdit ? '更新成功' : '创建成功')
    navigate(-1) // 或 navigate('/base')
  }

  return (
    <ProForm<any>
      onFinish={handleSubmit}
      submitter={{
        searchConfig: { submitText: isEdit ? '更新' : '创建' },
        resetButtonProps: false,
      }}
    >
      <ProForm.Group>
        <ProFormText
          name="code"
          label="编码"
          rules={[{ required: true, message: '请输入编码' }]}
          disabled={isEdit}
          width="md"
          placeholder="自动生成或手动输入"
        />
        <ProFormText
          name="name"
          label="名称"
          rules={[{ required: true, message: '请输入名称' }]}
          width="md"
          placeholder="请输入名称"
        />
      </ProForm.Group>

      <ProForm.Group>
        <ProFormSelect
          name="type"
          label="类型"
          width="md"
          options={[
            { label: '类型一', value: 'type1' },
            { label: '类型二', value: 'type2' },
          ]}
          placeholder="请选择类型"
        />
        <ProFormText
          name="contact"
          label="联系人"
          width="md"
          placeholder="请输入联系人"
        />
      </ProForm.Group>

      <ProForm.Group>
        <ProFormDigit
          name="sort"
          label="排序"
          min={1}
          max={999}
          width="md"
          fieldProps={{ precision: 0 }}
        />
        <ProFormText
          name="phone"
          label="电话"
          width="md"
          placeholder="请输入电话"
        />
      </ProForm.Group>

      <ProFormTextArea
        name="remark"
        label="备注"
        width="xl"
        placeholder="请输入备注"
      />
    </ProForm>
  )
}
