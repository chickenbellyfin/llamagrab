import { PageHeader } from 'antd';
import { useNavigate } from 'react-router-dom';
import ContentWrapper from '../components/ContentWrapper';
import RegionStatusSection from '../components/RegionStatusSection';

export default function RegionsPage() {
  const navigate = useNavigate();
  return (
    <ContentWrapper>
      <PageHeader
          title={<span className="ui-title">Region Statuses</span>}
          onBack={() => navigate('/')}/>
      <RegionStatusSection/>
    </ContentWrapper>
  );
};