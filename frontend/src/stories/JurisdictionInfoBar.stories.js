import JurisdictionInfoBar from '../components/JurisdictionInfoBar';

export default {
  title: 'Nyaya UI Kit/Jurisdiction/JurisdictionInfoBar',
  component: JurisdictionInfoBar,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export const India = {
  args: {
    country: 'India',
    courtSystem: 'District Court System',
    authorityFraming: 'Constitutional framework under Article 14 (equality) and Article 21 (life and liberty)',
    emergencyGuidance: 'Contact local police at 100 or legal aid at 15100 for immediate assistance'
  },
};

export const MissingData = {
  args: {
    country: '',
    courtSystem: '',
    authorityFraming: '',
    emergencyGuidance: ''
  },
};

export const UAE = {
  args: {
    country: 'United Arab Emirates',
    courtSystem: 'Federal Court System',
    authorityFraming: 'Civil law system based on Islamic Sharia principles and codified laws',
    emergencyGuidance: 'Call 999 for police or 800-5000 for legal consultation'
  },
};