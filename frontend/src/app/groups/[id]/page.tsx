import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { SavingsGroup, Investment, Contribution } from '@/types';
import { groupsApi, investmentsApi, contributionsApi } from '@/lib/api';
import Link from 'next/link';

type ChartData = {
  labels: string[];
  values: number[];
};

export default function GroupDetail() {
  const params = useParams();
  const groupId = parseInt(params.id as string, 10);
  
  const [group, setGroup] = useState<SavingsGroup | null>(null);
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [contributionForm, setContributionForm] = useState({
    amount: '',
    transaction_type: 'DEPOSIT',
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [groupRes, investmentsRes, contributionsRes] = await Promise.all([
          groupsApi.getDetails(groupId),
          investmentsApi.list(groupId),
          contributionsApi.list(groupId),
        ]);

        setGroup(groupRes.data);
        setInvestments(investmentsRes.data);
        setContributions(contributionsRes.data);
      } catch (err) {
        setError('Failed to load group details');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [groupId]);

  const handleContribution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!group) return;

    try {
      await contributionsApi.create(groupId, {
        amount: parseFloat(contributionForm.amount),
        transaction_type: contributionForm.transaction_type as 'DEPOSIT' | 'WITHDRAWAL',
      });
      
      // Refresh contributions
      const contributionsRes = await contributionsApi.list(groupId);
      setContributions(contributionsRes.data);
      
      // Reset form
      setContributionForm({ amount: '', transaction_type: 'DEPOSIT' });
    } catch (err) {
      setError('Failed to process contribution');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!group) return <div>Group not found</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto lg:max-w-none">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">
              {group.name}
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              {group.description || 'No description available'}
            </p>
          </div>
          <div className="mt-4 md:mt-0">
            <span className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
              group.risk_tolerance === 'LOW' ? 'bg-green-100 text-green-800' :
              group.risk_tolerance === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {group.risk_tolerance} Risk
            </span>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Group Statistics</h3>
            <dl className="mt-4 space-y-4">
              <div className="flex items-baseline justify-between">
                <dt className="text-sm font-medium text-gray-500">Total Balance</dt>
                <dd className="text-2xl font-semibold text-purple-600">
                  ${group.total_balance.toLocaleString()}
                </dd>
              </div>
              <div className="flex items-baseline justify-between">
                <dt className="text-sm font-medium text-gray-500">Members</dt>
                <dd className="text-2xl font-semibold text-purple-600">
                  {group.members.length}
                </dd>
              </div>
              <div className="flex items-baseline justify-between">
                <dt className="text-sm font-medium text-gray-500">Tier Level</dt>
                <dd className="text-2xl font-semibold text-purple-600">
                  {group.tier_level}
                </dd>
              </div>
            </dl>
          </div>

          {/* Contribution Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Make a Contribution</h3>
            <form onSubmit={handleContribution} className="mt-4 space-y-4">
              <div>
                <label htmlFor="amount" className="block text-sm font-medium text-gray-700">
                  Amount
                </label>
                <div className="mt-1">
                  <input
                    type="number"
                    name="amount"
                    id="amount"
                    required
                    min="0"
                    step="0.01"
                    value={contributionForm.amount}
                    onChange={(e) => setContributionForm(prev => ({ ...prev, amount: e.target.value }))}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="transaction_type" className="block text-sm font-medium text-gray-700">
                  Transaction Type
                </label>
                <select
                  id="transaction_type"
                  name="transaction_type"
                  value={contributionForm.transaction_type}
                  onChange={(e) => setContributionForm(prev => ({ ...prev, transaction_type: e.target.value }))}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                >
                  <option value="DEPOSIT">Deposit</option>
                  <option value="WITHDRAWAL">Withdrawal</option>
                </select>
              </div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                Submit
              </button>
            </form>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
            <div className="mt-4 flow-root">
              <ul role="list" className="-my-4 divide-y divide-gray-200">
                {contributions.slice(0, 5).map((contribution) => (
                  <li key={contribution.id} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-900">
                          {contribution.transaction_type === 'DEPOSIT' ? 'Deposit' : 'Withdrawal'}
                        </p>
                        <p className="truncate text-sm text-gray-500">
                          ${contribution.amount.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <span className={`inline-flex rounded-full px-2 text-xs font-semibold ${
                          contribution.transaction_type === 'DEPOSIT'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {contribution.transaction_type}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Investments Section */}
        <div className="mt-8">
          <div className="sm:flex sm:items-center">
            <div className="sm:flex-auto">
              <h3 className="text-lg font-medium text-gray-900">Group Investments</h3>
              <p className="mt-2 text-sm text-gray-700">
                Overview of all investments made by this group.
              </p>
            </div>
            {group.tier_level > 1 && (
              <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
                <Link
                  href={`/groups/${groupId}/investments/create`}
                  className="block rounded-md bg-purple-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-purple-500"
                >
                  New Investment
                </Link>
              </div>
            )}
          </div>
          <div className="mt-4 flow-root">
            <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead>
                    <tr>
                      <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Type</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Amount</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Current Value</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Return Rate</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Provider</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {investments.map((investment) => (
                      <tr key={investment.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">
                          {investment.investment_type}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          ${investment.amount.toLocaleString()}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          ${investment.current_value.toLocaleString()}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {investment.annual_return_rate}%
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {investment.provider}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
