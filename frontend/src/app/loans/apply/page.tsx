import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { loansApi } from '@/lib/api';

export default function ApplyLoan() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    amount: '',
    interest_rate: '',
    due_date: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await loansApi.create({
        amount: parseFloat(formData.amount),
        interest_rate: parseFloat(formData.interest_rate),
        due_date: formData.due_date,
      });
      router.push('/loans');
    } catch (err) {
      setError('Failed to submit loan application. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="space-y-12">
        <div className="pb-12">
          <h2 className="text-base font-semibold leading-7 text-gray-900">Apply for a Loan</h2>
          <p className="mt-1 text-sm leading-6 text-gray-600">
            Fill out the form below to submit your loan application.
          </p>

          {error && (
            <div className="mt-4 rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{error}</h3>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-10 space-y-8">
            <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
              <div className="sm:col-span-4">
                <label htmlFor="amount" className="block text-sm font-medium leading-6 text-gray-900">
                  Loan Amount
                </label>
                <div className="mt-2">
                  <input
                    type="number"
                    name="amount"
                    id="amount"
                    required
                    min="0"
                    step="0.01"
                    value={formData.amount}
                    onChange={handleChange}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>

              <div className="sm:col-span-2">
                <label htmlFor="interest_rate" className="block text-sm font-medium leading-6 text-gray-900">
                  Interest Rate (%)
                </label>
                <div className="mt-2">
                  <input
                    type="number"
                    name="interest_rate"
                    id="interest_rate"
                    required
                    min="0"
                    step="0.01"
                    value={formData.interest_rate}
                    onChange={handleChange}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>

              <div className="sm:col-span-4">
                <label htmlFor="due_date" className="block text-sm font-medium leading-6 text-gray-900">
                  Due Date
                </label>
                <div className="mt-2">
                  <input
                    type="date"
                    name="due_date"
                    id="due_date"
                    required
                    value={formData.due_date}
                    onChange={handleChange}
                    min={new Date().toISOString().split('T')[0]}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-x-6">
              <button
                type="button"
                onClick={() => router.back()}
                className="text-sm font-semibold leading-6 text-gray-900"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600"
              >
                {loading ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
