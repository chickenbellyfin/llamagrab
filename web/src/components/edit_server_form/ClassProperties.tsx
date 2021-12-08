import { Card } from "antd";
import { ModProperty } from "../../api"
import { ClassPropertiesSpecSet } from "../../data";
import ModPropertyList from "./ModPropertyList";

type ClassPropertiesProps = {
  classLabel: string,
  classProperties?: ModProperty[]
  onChange: (value: ModProperty[]) => void
}
export default function ClassProperties({ classLabel, classProperties, onChange}: ClassPropertiesProps) {

  const setProperties = (value: ModProperty[]) => {
    onChange(value)
  }

  return (
    <Card 
      headStyle={{backgroundColor: 'rgba(0,0,0,.1)'}}
      className='form-card' 
      title={`${classLabel} Class Properties`}
      >
      <ModPropertyList
        properties={classProperties}
        specSet={ClassPropertiesSpecSet}
        onChange={setProperties}/>
  </Card>);
}
