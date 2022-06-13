import { Card } from "antd";
import { ClassPropertiesSpecSet, ModPropertySpecSet, ValueModsSpecSet } from "../../data";
import { ModProperty } from "../../domain";
import ModPropertyList from "./ModPropertyList";

type ClassPropertiesBuilderProps = {
  title: string
  specSet: ModPropertySpecSet
}

type ClassPropertiesProps = {
  classLabel: string,
  classProperties?: ModProperty[]
  onChange: (value: ModProperty[]) => void
}

function ClassPropertiesBuilder({title, specSet}: ClassPropertiesBuilderProps) {
  return function ClassPropertiesComponent({ classLabel, classProperties, onChange}: ClassPropertiesProps) {

    const setProperties = (value: ModProperty[]) => {
      onChange(value)
    }

    return (
      <Card
        headStyle={{backgroundColor: 'rgba(0,0,0,.1)'}}
        className='form-card'
        title={`${classLabel} ${title}`}
        >
        <ModPropertyList
          properties={classProperties}
          specSet={specSet}
          onChange={setProperties}/>
    </Card>);
  }
}

export const ClassProperties = ClassPropertiesBuilder({
  title: 'Class Properties',
  specSet: ClassPropertiesSpecSet
});

export const ClassValueMods = ClassPropertiesBuilder({
  title: 'Class Value Mods',
  specSet: ValueModsSpecSet
});
