import { useState, useEffect } from 'react';
import { assetsAPI } from '../services/api';

const AssetForm = ({ asset, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    asset_code: '',
    name: '',
    serial_number: '',
    category_id: '',
    current_status: 'active',
    asset_condition: '',
    description: '',
    pic_user_id: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (asset) {
      setFormData({
        asset_code: asset.asset_code || '',
        name: asset.name || '',
        serial_number: asset.serial_number || '',
        category_id: asset.category_id || '',
        current_status: asset.current_status || 'active',
        asset_condition: asset.asset_condition || '',
        description: asset.description || '',
        pic_user_id: asset.pic_user_id || '',
      });
    }
  }, [asset]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = {
        ...formData,
        category_id: formData.category_id || undefined,
        pic_user_id: formData.pic_user_id || undefined,
      };

      if (asset) {
        await assetsAPI.updateAsset(asset.id, data);
      } else {
        await assetsAPI.createAsset(data);
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save asset');
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
            Asset Code *
          </label>
          <input
            type="text"
            value={formData.asset_code}
            onChange={(e) => setFormData({ ...formData, asset_code: e.target.value })}
            className="input-field"
            required
            disabled={!!asset}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Serial Number *
          </label>
          <input
            type="text"
            value={formData.serial_number}
            onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
            className="input-field"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Name *
        </label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="input-field"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Category ID *
          </label>
          <input
            type="text"
            value={formData.category_id}
            onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
            className="input-field"
            placeholder="UUID"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Status
          </label>
          <select
            value={formData.current_status}
            onChange={(e) => setFormData({ ...formData, current_status: e.target.value })}
            className="input-field"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Maintenance</option>
            <option value="decommissioned">Decommissioned</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Asset Condition
        </label>
        <input
          type="text"
          value={formData.asset_condition}
          onChange={(e) => setFormData({ ...formData, asset_condition: e.target.value })}
          className="input-field"
          placeholder="excellent, good, fair, poor"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="input-field"
          rows="3"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          PIC User ID
        </label>
        <input
          type="text"
          value={formData.pic_user_id}
          onChange={(e) => setFormData({ ...formData, pic_user_id: e.target.value })}
          className="input-field"
          placeholder="UUID (optional)"
        />
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
          {loading ? 'Saving...' : asset ? 'Update Asset' : 'Create Asset'}
        </button>
      </div>
    </form>
  );
};

export default AssetForm;

