// Testing
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import userClient from '../services/userClient';

vi.mock('../services/userClient');

test('renders users', async () => {
  userClient.listUsers.mockResolvedValue({
    usersList: [{id: '1', name: 'John', email: 'john@test.com'}],
    totalCount: 1
  });
  render(<UserList />);
  await waitFor(() => expect(screen.getByText('John')).toBeInTheDocument());
});
