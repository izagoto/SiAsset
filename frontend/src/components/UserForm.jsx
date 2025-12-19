import { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';

const UserForm = ({ user, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role_id: '',
    is_active: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        password: '',
        role_id: user.role_id || '',
        is_active: user.is_active ?? true,
      });
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = { ...formData };
      if (user && !data.password) {
        delete data.password;
      }

      if (user) {
        await usersAPI.updateUser(user.id, data);
      } else {
        await usersAPI.createUser(data);
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Username *
          </label>
          <input
            type="text"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            className="input-field"
            required
            minLength={3}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Email *
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="input-field"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Password {user ? '(leave empty to keep current)' : '*'}
        </label>
        <input
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          className="input-field"
          required={!user}
          minLength={6}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Role ID *
          </label>
          <input
            type="text"
            value={formData.role_id}
            onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
            className="input-field"
            placeholder="UUID"
            required
          />
        </div>

        {user && (
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Status
            </label>
            <select
              value={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.value === 'true' })}
              className="input-field"
            >
              <option value={true}>Active</option>
              <option value={false}>Inactive</option>
            </select>
          </div>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <button
          type="button"
          onClick={onClose}
          className="btn-secondary"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={loading}
        >
          {loading ? 'Saving...' : user ? 'Update User' : 'Create User'}
        </button>
      </div>
    </form>
  );
};

export default UserForm;

