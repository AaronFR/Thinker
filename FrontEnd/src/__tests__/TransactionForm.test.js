     // TransactionForm.test.js
     import React from 'react';
     import { render, screen, fireEvent, waitFor } from '@testing-library/react';
     import TransactionForm from '../components/TransactionForm' 
     import { apiFetch } from '../utils/authUtils';
   
     jest.mock('../utils/authUtils');
   
     describe('TransactionForm Component', () => {
         const mockOnSuccess = jest.fn();
   
         beforeEach(() => {
             jest.clearAllMocks();
         });
   
         test('renders the form correctly', () => {
             render(<TransactionForm onSuccess={mockOnSuccess} />);
             expect(screen.getByLabelText(/amount in dollars/i)).toBeInTheDocument();
             expect(screen.getByRole('button', { name: /pay/i })).toBeInTheDocument();
         });
   
         test('validates input and displays error for invalid amount', async () => {
             render(<TransactionForm onSuccess={mockOnSuccess} />);
             const amountInput = screen.getByLabelText(/amount in dollars/i);
             const payButton = screen.getByRole('button', { name: /pay/i });
   
             fireEvent.change(amountInput, { target: { value: '-50' } });
             fireEvent.click(payButton);
   
             expect(await screen.findByRole('alert')).toHaveTextContent('Please enter a valid positive amount.');
         });
   
         test('submits the form successfully', async () => {
             apiFetch.mockResolvedValueOnce({ ok: true });
   
             render(<TransactionForm onSuccess={mockOnSuccess} />);
             const amountInput = screen.getByLabelText(/amount in dollars/i);
             const payButton = screen.getByRole('button', { name: /pay/i });
   
             fireEvent.change(amountInput, { target: { value: '50' } });
             fireEvent.click(payButton);
   
             expect(payButton).toHaveTextContent('Processing...');
   
             await waitFor(() => expect(apiFetch).toHaveBeenCalledTimes(1));
             expect(await screen.findByRole('status')).toHaveTextContent('Your balance has been successfully updated.');
             expect(mockOnSuccess).toHaveBeenCalled();
             expect(payButton).toHaveTextContent('Pay');
         });
   
         test('handles API failure gracefully', async () => {
             apiFetch.mockResolvedValueOnce({ ok: false, json: async () => ({ message: 'Insufficient funds.' }) });
   
             render(<TransactionForm onSuccess={mockOnSuccess} />);
             const amountInput = screen.getByLabelText(/amount in dollars/i);
             const payButton = screen.getByRole('button', { name: /pay/i });
   
             fireEvent.change(amountInput, { target: { value: '50' } });
             fireEvent.click(payButton);
   
             expect(payButton).toHaveTextContent('Processing...');
   
             await waitFor(() => expect(apiFetch).toHaveBeenCalledTimes(1));
             // ToDo: Theres a point to be made that you should have specific errors if the transaction files, but wait for stripe integration first.
             expect(await screen.findByRole('alert')).toHaveTextContent('There was an issue processing your transaction. Please try again.');
             expect(payButton).toHaveTextContent('Pay');
         });
   
         test('handles network error gracefully', async () => {
             apiFetch.mockRejectedValueOnce(new Error('Network Error'));
   
             render(<TransactionForm onSuccess={mockOnSuccess} />);
             const amountInput = screen.getByLabelText(/amount in dollars/i);
             const payButton = screen.getByRole('button', { name: /pay/i });
   
             fireEvent.change(amountInput, { target: { value: '50' } });
             fireEvent.click(payButton);
   
             expect(payButton).toHaveTextContent('Processing...');
   
             await waitFor(() => expect(apiFetch).toHaveBeenCalledTimes(1));
             expect(await screen.findByRole('alert')).toHaveTextContent('There was an issue processing your transaction. Please try again.');
             expect(payButton).toHaveTextContent('Pay');
         });
     });
     