import { Card } from "antd";
import { ModPropertySpecSet, VehiclePropertiesSpecSet } from "../../data";
import { ModProperty } from "../../domain";
import ModPropertyList from "./ModPropertyList";

type VehiclePropertiesBuilderProps = {
  title: string
  specSet: ModPropertySpecSet
}

type VehiclePropertiesProps = {
  vehicleLabel: string,
  vehicleProperties?: ModProperty[]
  onChange: (value: ModProperty[]) => void
}

function VehiclePropertiesBuilder({title, specSet}: VehiclePropertiesBuilderProps) {
  return function VehiclePropertiesComponent({ vehicleLabel, vehicleProperties, onChange}: VehiclePropertiesProps) {

    const setProperties = (value: ModProperty[]) => {
      onChange(value)
    }

    return (
      <Card
        headStyle={{backgroundColor: 'rgba(0,0,0,.1)'}}
        className='form-card'
        title={`${vehicleLabel} ${title}`}
        >
        <ModPropertyList
          properties={vehicleProperties}
          specSet={specSet}
          onChange={setProperties}/>
    </Card>);
  }
}

export const VehicleProperties = VehiclePropertiesBuilder({
  title: 'Vehicle Properties',
  specSet: VehiclePropertiesSpecSet
});
