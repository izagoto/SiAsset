import { useState, useEffect } from 'react';
import { assetsAPI, loansAPI } from '../services/api';
import { Package, TrendingUp, Clock, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalAssets: 0,
    assetsOnLoan: 0,
    pendingLoans: 0,
    overdueLoans: 0,
  });
  const [recentLoans, setRecentLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setError(null);
      setLoading(true);
      
      const [assetsRes, loansRes] = await Promise.all([
        assetsAPI.getAssets({ limit: 1 }).catch(err => {
          console.warn('Error fetching assets:', err);
          return { data: { data: { total: 0, items: [] } } };
        }),
        loansAPI.getLoans().catch(err => {
          console.warn('Error fetching loans:', err);
          // If 404, return empty array instead of throwing
          if (err.response?.status === 404) {
            return { data: { data: [] } };
          }
          return { data: { data: [] } };
        }),
      ]);

      const totalAssets = assetsRes.data.data?.total || 0;
      // Handle both array and object response formats
      let loans = [];
      if (Array.isArray(loansRes.data.data)) {
        loans = loansRes.data.data;
      } else if (loansRes.data.data?.items) {
        loans = loansRes.data.data.items;
      }
      
      const activeLoans = loans.filter(loan => 
        ['borrowed', 'approved'].includes((loan.loan_status || '').toLowerCase())
      );
      const pendingLoans = loans.filter(loan => 
        (loan.loan_status || '').toLowerCase() === 'pending'
      );
      const overdueLoans = loans.filter(loan => 
        (loan.loan_status || '').toLowerCase() === 'overdue'
      );

      setStats({
        totalAssets,
        assetsOnLoan: activeLoans.length,
        pendingLoans: pendingLoans.length,
        overdueLoans: overdueLoans.length,
      });

      setRecentLoans(loans.slice(0, 5));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError(error.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };


  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusBadge = (status) => {
    const statusLower = (status || '').toLowerCase();
    const statusConfig = {
      active: { color: 'bg-green-500/20 text-green-400', label: 'Active' },
      pending: { color: 'bg-yellow-500/20 text-yellow-400', label: 'Pending' },
      overdue: { color: 'bg-red-500/20 text-red-400', label: 'Overdue' },
      returned: { color: 'bg-blue-500/20 text-blue-400', label: 'Returned' },
      borrowed: { color: 'bg-green-500/20 text-green-400', label: 'Borrowed' },
      approved: { color: 'bg-blue-500/20 text-blue-400', label: 'Approved' },
      rejected: { color: 'bg-red-500/20 text-red-400', label: 'Rejected' },
    };

    const config = statusConfig[statusLower] || statusConfig.pending;
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-white text-lg">Loading dashboard data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {!loading && !error && stats.totalAssets === 0 && recentLoans.length === 0 && (
        <div className="bg-blue-500/10 border border-blue-500/50 text-blue-400 px-4 py-3 rounded-lg">
          <p className="font-medium mb-1">No data available</p>
          <p className="text-sm">Start by creating assets and loan requests to see dashboard statistics.</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <Package className="text-blue-400" size={24} />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-white mb-1">{stats.totalAssets.toLocaleString()}</h3>
          <p className="text-slate-400 text-sm">Total Assets</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-500/20 rounded-lg">
              <TrendingUp className="text-green-400" size={24} />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-white mb-1">{stats.assetsOnLoan}</h3>
          <p className="text-slate-400 text-sm">Assets on Loan</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-yellow-500/20 rounded-lg">
              <Clock className="text-yellow-400" size={24} />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-white mb-1">{stats.pendingLoans}</h3>
          <p className="text-slate-400 text-sm">Pending Loans</p>
          <p className="text-yellow-400 text-xs mt-1">Awaiting approval</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-red-500/20 rounded-lg">
              <CheckCircle className="text-red-400" size={24} />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-white mb-1">{stats.overdueLoans}</h3>
          <p className="text-slate-400 text-sm">Overdue Loans</p>
          <p className="text-red-400 text-xs mt-1">Requires attention</p>
        </div>
      </div>


      {/* Recent Asset Loans */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Recent Asset Loans</h2>
          <button 
            onClick={() => navigate('/loans')}
            className="text-blue-400 hover:text-blue-300 text-sm"
          >
            View All Loans
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="table-header">
              <tr>
                <th className="text-left py-3 px-4">STATUS</th>
                <th className="text-left py-3 px-4">BORROWER</th>
                <th className="text-left py-3 px-4">ASSET</th>
                <th className="text-left py-3 px-4">DUE DATE</th>
                <th className="text-left py-3 px-4">ACTION</th>
              </tr>
            </thead>
            <tbody>
              {recentLoans.length > 0 ? (
                recentLoans.map((loan) => (
                  <tr key={loan.id} className="table-row">
                    <td className="py-3 px-4">{getStatusBadge(loan.loan_status?.toLowerCase())}</td>
                    <td className="py-3 px-4 text-slate-300">
                      {loan.user_id ? `User ${loan.user_id.slice(0, 8)}` : 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-white">
                      {loan.asset_id ? `Asset ${loan.asset_id.slice(0, 8)}` : 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-slate-300">{formatDate(loan.due_date)}</td>
                    <td className="py-3 px-4">
                      <button 
                        onClick={() => navigate('/loans')}
                        className="text-blue-400 hover:text-blue-300 text-sm"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-slate-400">
                    No loans found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default Dashboard;

