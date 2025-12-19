import { useState, useEffect } from 'react';
import { assetsAPI } from '../services/api';
import { Plus, Eye, Edit, Trash2 } from 'lucide-react';
import Modal from '../components/Modal';
import AssetForm from '../components/AssetForm';
import DataTable from '../components/DataTable';

const Assets = () => {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [total, setTotal] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [viewAsset, setViewAsset] = useState(null);

  useEffect(() => {
    fetchAssets();
  }, [statusFilter, categoryFilter]);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const params = {
        skip: 0,
        limit: 1000, // Fetch all for client-side pagination
      };
      
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category_id = categoryFilter;

      const response = await assetsAPI.getAssets(params);
      setAssets(response.data.data.items || []);
      setTotal(response.data.data.total || 0);
    } catch (error) {
      console.error('Error fetching assets:', error);
      // Set empty arrays on any error
      setAssets([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'bg-green-500/20 text-green-400', label: 'Active' },
      inactive: { color: 'bg-gray-500/20 text-gray-400', label: 'Inactive' },
      maintenance: { color: 'bg-yellow-500/20 text-yellow-400', label: 'Maintenance' },
      decommissioned: { color: 'bg-red-500/20 text-red-400', label: 'Decommissioned' },
    };

    const config = statusConfig[status] || statusConfig.active;
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };


  const handleCreate = () => {
    setSelectedAsset(null);
    setShowModal(true);
  };

  const handleEdit = (asset) => {
    setSelectedAsset(asset);
    setShowModal(true);
  };

  const handleView = async (assetId) => {
    try {
      const response = await assetsAPI.getAsset(assetId);
      setViewAsset(response.data.data);
    } catch (error) {
      console.error('Error fetching asset:', error);
      alert(error.response?.data?.message || 'Failed to fetch asset details');
    }
  };

  const handleDelete = async (assetId) => {
    if (window.confirm('Are you sure you want to delete this asset?')) {
      try {
        await assetsAPI.deleteAsset(assetId);
        fetchAssets();
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to delete asset');
      }
    }
  };

  const handleSuccess = () => {
    fetchAssets();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <nav className="text-sm text-slate-400 mb-2">
          <span>Home</span> / <span>Assets</span> / <span className="text-white">Asset List</span>
        </nav>
        <h1 className="text-3xl font-bold text-white mb-2">Assets</h1>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-2xl font-bold text-white mb-1">{total.toLocaleString()}</h3>
          <p className="text-slate-400 text-sm">Total Assets</p>
        </div>
        <div className="card">
          <h3 className="text-2xl font-bold text-white mb-1">
            {assets.filter(a => a.current_status === 'active').length}
          </h3>
          <p className="text-slate-400 text-sm">Active Assets</p>
        </div>
        <div className="card">
          <h3 className="text-2xl font-bold text-white mb-1">
            {assets.filter(a => a.current_status === 'maintenance').length}
          </h3>
          <p className="text-slate-400 text-sm">In Maintenance</p>
        </div>
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
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Maintenance</option>
            <option value="decommissioned">Decommissioned</option>
          </select>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="input-field"
          >
            <option value="">All Categories</option>
          </select>
          <button onClick={handleCreate} className="btn-primary flex items-center gap-2">
            <Plus size={18} />
            Add Asset
          </button>
        </div>
      </div>

      {/* DataTable */}
      <DataTable
        columns={[
          {
            header: 'ASSET CODE',
            accessor: 'asset_code',
            cell: (row) => <div className="text-white font-medium">{row.asset_code}</div>,
          },
          {
            header: 'NAME',
            accessor: 'name',
            cell: (row) => <div className="text-white font-medium">{row.name}</div>,
          },
          {
            header: 'SERIAL NUMBER',
            accessor: 'serial_number',
            cell: (row) => <span className="text-slate-300">{row.serial_number || 'N/A'}</span>,
          },
          {
            header: 'CONDITION',
            accessor: 'asset_condition',
            cell: (row) => <span className="text-slate-300">{row.asset_condition || 'N/A'}</span>,
          },
          {
            header: 'PIC USER',
            accessor: 'pic_user_id',
            cell: (row) => (
              <span className="text-slate-300">
                {row.pic_user_id ? `User ${row.pic_user_id.slice(0, 8)}` : 'Unassigned'}
              </span>
            ),
          },
          {
            header: 'STATUS',
            accessor: 'current_status',
            cell: (row) => getStatusBadge(row.current_status),
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
                <button
                  onClick={() => handleEdit(row)}
                  className="text-slate-400 hover:text-slate-300"
                  title="Edit"
                >
                  <Edit size={18} />
                </button>
                <button
                  onClick={() => handleDelete(row.id)}
                  className="text-red-400 hover:text-red-300"
                  title="Delete"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ),
          },
        ]}
        data={assets}
        loading={loading}
        searchPlaceholder="Search by name, code, or serial number"
        defaultPageSize={10}
      />

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedAsset(null);
        }}
        title={selectedAsset ? 'Edit Asset' : 'Create New Asset'}
      >
        <AssetForm
          asset={selectedAsset}
          onClose={() => {
            setShowModal(false);
            setSelectedAsset(null);
          }}
          onSuccess={handleSuccess}
        />
      </Modal>

      {/* View Modal */}
      {viewAsset && (
        <Modal
          isOpen={!!viewAsset}
          onClose={() => setViewAsset(null)}
          title="Asset Details"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-slate-400">Asset Code</label>
                <p className="text-white font-medium">{viewAsset.asset_code}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Serial Number</label>
                <p className="text-white font-medium">{viewAsset.serial_number}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Name</label>
                <p className="text-white font-medium">{viewAsset.name}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Status</label>
                <p className="text-white font-medium">{getStatusBadge(viewAsset.current_status)}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Condition</label>
                <p className="text-white font-medium">{viewAsset.asset_condition || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Created At</label>
                <p className="text-white font-medium">
                  {new Date(viewAsset.created_at).toLocaleString('id-ID')}
                </p>
              </div>
            </div>
            {viewAsset.description && (
              <div>
                <label className="text-sm text-slate-400">Description</label>
                <p className="text-white">{viewAsset.description}</p>
              </div>
            )}
            <div className="flex justify-end pt-4">
              <button onClick={() => setViewAsset(null)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Assets;

