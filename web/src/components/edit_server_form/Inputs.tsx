import { InfoCircleOutlined } from "@ant-design/icons";
import { InputNumber } from "antd";

export function InputInteger({ ...props }) {
  return <InputNumber precision={0} style={{width: '100%'}} {...props}/>
}

export function InputFloat({...props}) {
  return <InputNumber precision={2} style={{width: '100%'}} {...props}/>
}

type InputPercentProps = {
  value?: number
  defaultValue?: number
  min?: number
  max?: number
  onChange: (value: number) => void
}


function toPercent(v: number) { return Math.round(v * 100.0) }

export function InputPercent({value, defaultValue, min, max, onChange, ...props}: InputPercentProps) {

  return <InputNumber<number>
    defaultValue={defaultValue && toPercent(defaultValue)}
    value={value && toPercent(value)}
    onChange={value => onChange(value / 100.0)}
    min={min && toPercent(min)}
    max={max && toPercent(max)}
    formatter={value => (value && `${value}%`) || ''}
    parser={value => (value && parseInt(value.replace('%', ''))) || 100 }
  />
}

type HintProps = {
  text: string
}
export function Hint({text}: HintProps) {
  return <span style={{opacity:'70%'}}><InfoCircleOutlined/> {text}</span>
}