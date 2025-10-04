import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { SavingsGroup, Investment, Loan } from '@/types';
import { groupsApi, investmentsApi, loansApi } from '@/lib/api';

type Activity = {
  id: number;
  type: 'LOAN' | 'INVESTMENT';
  amount: number;
  status?: string;
  date: string;
  details: {
    type?: string;
    value?: number;
    dueDate?: string;
  };
};

export default function Dashboard() {
  const { user } = useAuth();
  const [groups, setGroups] = useState<SavingsGroup[]>([]);
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [groupsRes, loansRes] = await Promise.all([
          groupsApi.list(),
          loansApi.list(),
        ]);

        setGroups(groupsRes.data);
        setLoans(loansRes.data);

        // Fetch investments for each group
        const investmentPromises = groupsRes.data.map((group: SavingsGroup) => 
          investmentsApi.list(group.id)
        );
        
        const investmentResponses = await Promise.all(investmentPromises);
        const allInvestments = investmentResponses.flatMap(res => res.data);
        setInvestments(allInvestments);

        // Combine loans and investments into activities
        const combinedActivities: Activity[] = [
          ...loansRes.data.map((loan: Loan) => ({
            id: loan.id,
            type: 'LOAN' as const,
            amount: loan.amount,
            status: loan.status,
            date: loan.created_at,
            details: {
              dueDate: loan.due_date,
            },
          })),
          ...allInvestments.map((investment: Investment) => ({
            id: investment.id,
            type: 'INVESTMENT' as const,
            amount: investment.amount,
            date: investment.start_date,
            details: {
              type: investment.investment_type,
              value: investment.current_value,
            },
          })),
        ].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

        setActivities(combinedActivities);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-gray-900">
              Welcome back, {user?.username}!
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Here's an overview of your financial activity
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
              <dt className="text-sm font-medium text-gray-500">Total Groups</dt>
              <dd className="mt-1 text-3xl font-semibold text-purple-600">
                {groups.length}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
              <dt className="text-sm font-medium text-gray-500">Active Investments</dt>
              <dd className="mt-1 text-3xl font-semibold text-purple-600">
                {investments.length}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
              <dt className="text-sm font-medium text-gray-500">Total Investment Value</dt>
              <dd className="mt-1 text-3xl font-semibold text-purple-600">
                ${investments.reduce((sum, inv) => sum + inv.current_value, 0).toLocaleString()}
              </dd>
            </div>
            <div className="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
              <dt className="text-sm font-medium text-gray-500">Active Loans</dt>
              <dd className="mt-1 text-3xl font-semibold text-purple-600">
                {loans.filter(loan => loan.status === 'PENDING' || loan.status === 'APPROVED').length}
              </dd>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="mt-8">
            <h2 className="text-lg font-medium text-gray-900">Recent Activity</h2>
            <div className="mt-4 bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flow-root">
                  <ul role="list" className="-mb-8">
                {activities.slice(0, 5).map((activity, idx) => (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      <div className="relative flex space-x-3">
                        <div className="min-w-0 flex-1">
                          <div className="text-sm text-gray-500">
                            {activity.type === 'LOAN' ? (
                              <>
                                <span className="font-medium text-gray-900">Loan</span>
                                {' for '}
                                <span className="font-medium text-gray-900">${activity.amount}</span>
                                {activity.status && (
                                  <>
                                    {' - '}
                                    <span className={`inline-flex rounded-full px-2 text-xs font-semibold ${
                                      activity.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                                      activity.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-red-100 text-red-800'
                                    }`}>
                                      {activity.status}
                                    </span>
                                  </>
                                )}
                              </>
                            ) : (
                              <>
                                <span className="font-medium text-gray-900">Investment</span>
                                {' in '}
                                <span className="font-medium text-gray-900">{activity.details.type}</span>
                                {' - '}
                                <span className="text-green-600">${activity.details.value}</span>
                              </>
                            )}
                          </div>
                          <div className="mt-1 text-sm text-gray-500">
                            {activity.type === 'LOAN' && activity.details.dueDate ? (
                              <>Due {new Date(activity.details.dueDate).toLocaleDateString()}</>
                            ) : (
                              <>Started {new Date(activity.date).toLocaleDateString()}</>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
