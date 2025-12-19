import { useState, useEffect } from 'react';
import { loansAPI, assetsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Plus, CheckCircle, XCircle, Play, RotateCcw, Clock, Eye } from 'lucide-react';
import Modal from '../components/Modal';
import LoanForm from '../components/LoanForm';
import DataTable from '../components/DataTable';

const Loans = () => {
  const { user } = useAuth();
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [viewLoan, setViewLoan] = useState(null);
  const [assetsMap, setAssetsMap] = useState({});

  useEffect(() => {
    fetchLoans();
    fetchAssetsForLoans();
  }, [statusFilter]);

  const fetchAssetsForLoans = async () => {
    try {
      const response = await assetsAPI.getAssets({ limit: 1000 });
      const assets = response.data.data.items || [];
      const map = {};
      assets.forEach(asset => {
        map[asset.id] = asset;
      });
      setAssetsMap(map);
    } catch (error) {
      console.error('Error fetching assets:', error);
    }
  };

  const fetchLoans = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter) params.status_filter = statusFilter;

      const response = await loansAPI.getLoans(params);
      const loansData = Array.isArray(response.data.data) 
        ? response.data.data 
        : response.data.data?.items || [];
      setLoans(loansData);
    } catch (error) {
      console.error('Error fetching loans:', error);
      if (error.response?.status === 404) {
        setLoans([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (loanId) => {
    try {
      await loansAPI.approveLoan(loanId);
      fetchLoans();
    } catch (error) {
      console.error('Error approving loan:', error);
      alert(error.response?.data?.message || 'Failed to approve loan');
    }
  };

  const handleReject = async (loanId) => {
    try {
      await loansAPI.rejectLoan(loanId);
      fetchLoans();
    } catch (error) {
      console.error('Error rejecting loan:', error);
      alert(error.response?.data?.message || 'Failed to reject loan');
    }
  };

  const handleStart = async (loanId) => {
    try {
      await loansAPI.startBorrowing(loanId);
      fetchLoans();
    } catch (error) {
      console.error('Error starting borrowing:', error);
      alert(error.response?.data?.message || 'Failed to start borrowing');
    }
  };

  const handleReturn = async (loanId) => {
    try {
      await loansAPI.returnLoan(loanId);
      fetchLoans();
    } catch (error) {
      console.error('Error returning loan:', error);
      alert(error.response?.data?.message || 'Failed to return loan');
    }
  };

  const handleCreate = () => {
    setShowModal(true);
  };

  const handleView = async (loanId) => {
    try {
      const response = await loansAPI.getLoan(loanId);
      setViewLoan(response.data.data);
    } catch (error) {
      console.error('Error fetching loan:', error);
      alert(error.response?.data?.message || 'Failed to fetch loan details');
    }
  };

  const handleSuccess = () => {
    fetchLoans();
  };

  const getStatusBadge = (status) => {
    const statusLower = (status || '').toLowerCase();
    const statusConfig = {
      pending: { color: 'bg-yellow-500/20 text-yellow-400', label: 'Pending', icon: Clock },
      approved: { color: 'bg-blue-500/20 text-blue-400', label: 'Approved', icon: CheckCircle },
      rejected: { color: 'bg-red-500/20 text-red-400', label: 'Rejected', icon: XCircle },
      borrowed: { color: 'bg-green-500/20 text-green-400', label: 'Borrowed', icon: Play },
      returned: { color: 'bg-slate-500/20 text-slate-400', label: 'Returned', icon: RotateCcw },
      overdue: { color: 'bg-red-500/20 text-red-400', label: 'Overdue', icon: XCircle },
    };

    const config = statusConfig[statusLower] || statusConfig.pending;
    const Icon = config.icon;
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${config.color} flex items-center gap-1`}>
        <Icon size={14} />
        {config.label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const canApproveReject = user?.role_id;
  const isOwner = (loanUserId) => user?.id === loanUserId;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Loan Management</h1>
      </div>

      {/* Filters and Actions */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="borrowed">Borrowed</option>
            <option value="returned">Returned</option>
            <option value="overdue">Overdue</option>
          </select>
          <button onClick={handleCreate} className="btn-primary flex items-center gap-2">
            <Plus size={18} />
            New Loan Request
          </button>
        </div>
      </div>

      {/* DataTable */}
      <DataTable
        columns={[
          {
            header: 'STATUS',
            accessor: 'loan_status',
            cell: (row) => getStatusBadge(row.loan_status?.toLowerCase()),
          },
          {
            header: 'BORROWER',
            accessor: 'user_id',
            cell: (row) => (
              <span className="text-slate-300">
                {row.user_id ? `User ${row.user_id.slice(0, 8)}` : 'N/A'}
              </span>
            ),
          },
          {
            header: 'ASSET',
            accessor: 'asset_id',
            cell: (row) => (
              <div className="text-white">
                {assetsMap[row.asset_id]?.name || `Asset ${row.asset_id?.slice(0, 8) || 'N/A'}`}
                <div className="text-xs text-slate-400">
                  {assetsMap[row.asset_id]?.asset_code || ''}
                </div>
              </div>
            ),
          },
          {
            header: 'REQUESTED',
            accessor: 'requested_at',
            cell: (row) => (
              <span className="text-slate-300">{formatDate(row.requested_at)}</span>
            ),
          },
          {
            header: 'DUE DATE',
            accessor: 'due_date',
            cell: (row) => (
              <span className="text-slate-300">{formatDate(row.due_date)}</span>
            ),
          },
          {
            header: 'NOTES',
            accessor: 'notes',
            cell: (row) => (
              <span className="text-slate-400 text-sm max-w-xs truncate block">
                {row.notes || 'No notes'}
              </span>
            ),
          },
          {
            header: 'ACTIONS',
            accessor: 'id',
            cell: (row) => (
              <div className="flex gap-2">
                <button
                  onClick={() => handleView(row.id)}
                  className="text-blue-400 hover:text-blue-300"
                  title="View"
                >
                  <Eye size={18} />
                </button>
                {canApproveReject && (row.loan_status?.toLowerCase() === 'pending') && (
                  <>
                    <button
                      onClick={() => handleApprove(row.id)}
                      className="text-green-400 hover:text-green-300"
                      title="Approve"
                    >
                      <CheckCircle size={18} />
                    </button>
                    <button
                      onClick={() => handleReject(row.id)}
                      className="text-red-400 hover:text-red-300"
                      title="Reject"
                    >
                      <XCircle size={18} />
                    </button>
                  </>
                )}
                {isOwner(row.user_id) && (row.loan_status?.toLowerCase() === 'approved') && (
                  <button
                    onClick={() => handleStart(row.id)}
                    className="text-blue-400 hover:text-blue-300"
                    title="Start Borrowing"
                  >
                    <Play size={18} />
                  </button>
                )}
                {(isOwner(row.user_id) || canApproveReject) && 
                 ['borrowed', 'overdue'].includes(row.loan_status?.toLowerCase()) && (
                  <button
                    onClick={() => handleReturn(row.id)}
                    className="text-green-400 hover:text-green-300"
                    title="Return"
                  >
                    <RotateCcw size={18} />
                  </button>
                )}
              </div>
            ),
          },
        ]}
        data={loans}
        loading={loading}
        searchPlaceholder="Search loans..."
        defaultPageSize={10}
      />

      {/* Create Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create Loan Request"
      >
        <LoanForm
          onClose={() => setShowModal(false)}
          onSuccess={handleSuccess}
        />
      </Modal>

      {/* View Modal */}
      {viewLoan && (
        <Modal
          isOpen={!!viewLoan}
          onClose={() => setViewLoan(null)}
          title="Loan Details"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-slate-400">Status</label>
                <div className="mt-1">{getStatusBadge(viewLoan.loan_status)}</div>
              </div>
              <div>
                <label className="text-sm text-slate-400">Asset</label>
                <p className="text-white font-medium">
                  {assetsMap[viewLoan.asset_id]?.name || `Asset ${viewLoan.asset_id.slice(0, 8)}`}
                </p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Requested At</label>
                <p className="text-white font-medium">
                  {new Date(viewLoan.requested_at).toLocaleString('id-ID')}
                </p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Due Date</label>
                <p className="text-white font-medium">
                  {viewLoan.due_date ? new Date(viewLoan.due_date).toLocaleString('id-ID') : 'Open-ended'}
                </p>
              </div>
              {viewLoan.borrowed_at && (
                <div>
                  <label className="text-sm text-slate-400">Borrowed At</label>
                  <p className="text-white font-medium">
                    {new Date(viewLoan.borrowed_at).toLocaleString('id-ID')}
                  </p>
                </div>
              )}
              {viewLoan.returned_at && (
                <div>
                  <label className="text-sm text-slate-400">Returned At</label>
                  <p className="text-white font-medium">
                    {new Date(viewLoan.returned_at).toLocaleString('id-ID')}
                  </p>
                </div>
              )}
            </div>
            {viewLoan.notes && (
              <div>
                <label className="text-sm text-slate-400">Notes</label>
                <p className="text-white">{viewLoan.notes}</p>
              </div>
            )}
            <div className="flex justify-end pt-4">
              <button onClick={() => setViewLoan(null)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Loans;

