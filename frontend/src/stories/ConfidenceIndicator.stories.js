import ConfidenceIndicator from '../components/ConfidenceIndicator';

export default {
  title: 'Nyaya UI Kit/Trust/ConfidenceIndicator',
  component: ConfidenceIndicator,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export const High = {
  args: {
    confidence: 0.95,
  },
};

export const Medium = {
  args: {
    confidence: 0.65,
  },
};

export const Low = {
  args: {
    confidence: 0.35,
  },
};