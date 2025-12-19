import { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Plus, Eye, Edit, Trash2, UserCheck, UserX } from 'lucide-react';
import Modal from '../components/Modal';
import UserForm from '../components/UserForm';
import DataTable from '../components/DataTable';

const Users = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState('');
  const [total, setTotal] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [viewUser, setViewUser] = useState(null);

  useEffect(() => {
    if (currentUser?.role_id) {
      fetchUsers();
    }
  }, [roleFilter, currentUser]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = {
        skip: 0,
        limit: 1000, // Fetch all for client-side pagination
      };
      
      if (roleFilter) params.role_id = roleFilter;

      const response = await usersAPI.getUsers(params);
      setUsers(response.data.data.items || []);
      setTotal(response.data.data.total || 0);
    } catch (error) {
      console.error('Error fetching users:', error);
      if (error.response?.status === 404) {
        setUsers([]);
        setTotal(0);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (userId) => {
    try {
      await usersAPI.activateUser(userId);
      fetchUsers();
    } catch (error) {
      console.error('Error activating user:', error);
    }
  };

  const handleDeactivate = async (userId) => {
    try {
      await usersAPI.deactivateUser(userId);
      fetchUsers();
    } catch (error) {
      console.error('Error deactivating user:', error);
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await usersAPI.deleteUser(userId);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
        alert(error.response?.data?.message || 'Failed to delete user');
      }
    }
  };

  const handleCreate = () => {
    setSelectedUser(null);
    setShowModal(true);
  };

  const handleEdit = (user) => {
    setSelectedUser(user);
    setShowModal(true);
  };

  const handleView = async (userId) => {
    try {
      const response = await usersAPI.getUser(userId);
      setViewUser(response.data.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      alert(error.response?.data?.message || 'Failed to fetch user details');
    }
  };

  const handleSuccess = () => {
    fetchUsers();
  };

  const getStatusBadge = (isActive) => {
    if (isActive) {
      return (
        <span className="px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-400">
          Active
        </span>
      );
    }
    return (
      <span className="px-2 py-1 rounded text-xs font-medium bg-red-500/20 text-red-400">
        Inactive
      </span>
    );
  };

  const getRoleBadge = (roleId) => {
    // This would typically come from a roles API
    return (
      <span className="px-2 py-1 rounded text-xs font-medium bg-blue-500/20 text-blue-400">
        {roleId ? `Role ${roleId.slice(0, 8)}` : 'N/A'}
      </span>
    );
  };

  const isSuperAdmin = currentUser?.role_id;

  if (!isSuperAdmin) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400">You don't have permission to access this page.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <nav className="text-sm text-slate-400 mb-2">
          <span>Home</span> / <span>Settings</span> / <span className="text-white">User Management</span>
        </nav>
        <h1 className="text-3xl font-bold text-white mb-2">User Management</h1>
      </div>

      {/* Filters and Actions */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="input-field"
          >
            <option value="">All Roles</option>
          </select>
          <button onClick={handleCreate} className="btn-primary flex items-center gap-2">
            <Plus size={18} />
            Add New User
          </button>
        </div>
      </div>

      {/* DataTable */}
      <DataTable
        columns={[
          {
            header: 'USERNAME',
            accessor: 'username',
            cell: (row) => <div className="text-white font-medium">{row.username}</div>,
          },
          {
            header: 'EMAIL',
            accessor: 'email',
            cell: (row) => <span className="text-slate-300">{row.email}</span>,
          },
          {
            header: 'ROLE ID',
            accessor: 'role_id',
            cell: (row) => <span className="text-slate-300 text-sm">{row.role_id}</span>,
          },
          {
            header: 'STATUS',
            accessor: 'is_active',
            cell: (row) => getStatusBadge(row.is_active),
          },
          {
            header: 'CREATED AT',
            accessor: 'created_at',
            cell: (row) => (
              <span className="text-slate-300 text-sm">
                {new Date(row.created_at).toLocaleDateString('en-US')}
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
                <button
                  onClick={() => handleEdit(row)}
                  className="text-slate-400 hover:text-slate-300"
                  title="Edit"
                >
                  <Edit size={18} />
                </button>
                {row.is_active ? (
                  <button
                    onClick={() => handleDeactivate(row.id)}
                    className="text-yellow-400 hover:text-yellow-300"
                    title="Deactivate"
                  >
                    <UserX size={18} />
                  </button>
                ) : (
                  <button
                    onClick={() => handleActivate(row.id)}
                    className="text-green-400 hover:text-green-300"
                    title="Activate"
                  >
                    <UserCheck size={18} />
                  </button>
                )}
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
        data={users}
        loading={loading}
        searchPlaceholder="Search users..."
        defaultPageSize={10}
      />

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedUser(null);
        }}
        title={selectedUser ? 'Edit User' : 'Create New User'}
      >
        <UserForm
          user={selectedUser}
          onClose={() => {
            setShowModal(false);
            setSelectedUser(null);
          }}
          onSuccess={handleSuccess}
        />
      </Modal>

      {/* View Modal */}
      {viewUser && (
        <Modal
          isOpen={!!viewUser}
          onClose={() => setViewUser(null)}
          title="User Details"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-slate-400">Username</label>
                <p className="text-white font-medium">{viewUser.username}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Email</label>
                <p className="text-white font-medium">{viewUser.email}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Role ID</label>
                <p className="text-white font-medium">{viewUser.role_id}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Status</label>
                <p className="text-white font-medium">{getStatusBadge(viewUser.is_active)}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Created At</label>
                <p className="text-white font-medium">
                  {new Date(viewUser.created_at).toLocaleString('id-ID')}
                </p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Updated At</label>
                <p className="text-white font-medium">
                  {new Date(viewUser.updated_at).toLocaleString('id-ID')}
                </p>
              </div>
            </div>
            <div className="flex justify-end pt-4">
              <button onClick={() => setViewUser(null)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Users;

