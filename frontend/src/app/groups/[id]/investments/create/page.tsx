import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { investmentsApi } from '@/lib/api';

export default function CreateInvestment() {
  const router = useRouter();
  const params = useParams();
  const groupId = parseInt(params.id as string, 10);

  const [formData, setFormData] = useState({
    investment_type: 'UNIT_TRUST',
    amount: '',
    provider: '',
    annual_return_rate: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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
      await investmentsApi.create(groupId, {
        investment_type: formData.investment_type as 'UNIT_TRUST' | 'STOCKS' | 'BONDS' | 'REAL_ESTATE',
        amount: parseFloat(formData.amount),
        provider: formData.provider,
        annual_return_rate: parseFloat(formData.annual_return_rate),
      });
      router.push(`/groups/${groupId}`);
    } catch (err) {
      setError('Failed to create investment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="space-y-12">
        <div className="pb-12">
          <h2 className="text-base font-semibold leading-7 text-gray-900">Create New Investment</h2>
          <p className="mt-1 text-sm leading-6 text-gray-600">
            Add a new investment to your group's portfolio.
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
              <div className="sm:col-span-3">
                <label htmlFor="investment_type" className="block text-sm font-medium leading-6 text-gray-900">
                  Investment Type
                </label>
                <div className="mt-2">
                  <select
                    id="investment_type"
                    name="investment_type"
                    required
                    value={formData.investment_type}
                    onChange={handleChange}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                  >
                    <option value="UNIT_TRUST">Unit Trust</option>
                    <option value="STOCKS">Stocks</option>
                    <option value="BONDS">Bonds</option>
                    <option value="REAL_ESTATE">Real Estate</option>
                  </select>
                </div>
              </div>

              <div className="sm:col-span-3">
                <label htmlFor="amount" className="block text-sm font-medium leading-6 text-gray-900">
                  Amount
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

              <div className="sm:col-span-4">
                <label htmlFor="provider" className="block text-sm font-medium leading-6 text-gray-900">
                  Provider
                </label>
                <div className="mt-2">
                  <input
                    type="text"
                    name="provider"
                    id="provider"
                    required
                    value={formData.provider}
                    onChange={handleChange}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>

              <div className="sm:col-span-2">
                <label htmlFor="annual_return_rate" className="block text-sm font-medium leading-6 text-gray-900">
                  Annual Return Rate (%)
                </label>
                <div className="mt-2">
                  <input
                    type="number"
                    name="annual_return_rate"
                    id="annual_return_rate"
                    required
                    min="0"
                    step="0.01"
                    value={formData.annual_return_rate}
                    onChange={handleChange}
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
                {loading ? 'Creating...' : 'Create Investment'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
