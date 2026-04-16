import SessionStatus from '../components/SessionStatus';

export default {
  title: 'Nyaya UI Kit/Trust/SessionStatus',
  component: SessionStatus,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export const Active = {
  args: {
    status: 'active',
  },
};

export const Inactive = {
  args: {
    status: 'inactive',
  },
};

export const Expired = {
  args: {
    status: 'expired',
  },
};