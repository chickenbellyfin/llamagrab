import { PageHeader } from 'antd'
import ContentWrapper from '../components/ContentWrapper';
import RegionStatusSection from '../components/RegionStatusSection';

export default function RegionsPage() {
  return (
    <ContentWrapper>
      <PageHeader
          title={<span className="ui-title">Region Statuses</span>}/>
      <RegionStatusSection/>
    </ContentWrapper>
  );
};