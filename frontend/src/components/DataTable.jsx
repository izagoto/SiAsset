import { useState, useMemo, useEffect } from 'react';
import { ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

const DataTable = ({
  columns,
  data,
  loading = false,
  searchable = true,
  searchPlaceholder = 'Search...',
  showEntries = true,
  defaultPageSize = 10,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Handle sorting
  const handleSort = (columnKey) => {
    let direction = 'asc';
    if (sortConfig.key === columnKey && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key: columnKey, direction });
  };

  // Filter and sort data
  const filteredAndSortedData = useMemo(() => {
    let result = [...data];

    // Apply search filter
    if (searchTerm) {
      result = result.filter((row) => {
        return columns.some((column) => {
          const value = column.accessor
            ? typeof column.accessor === 'function'
              ? column.accessor(row)
              : row[column.accessor]
            : null;

          if (value === null || value === undefined) return false;

          return String(value)
            .toLowerCase()
            .includes(searchTerm.toLowerCase());
        });
      });
    }

    // Apply sorting
    if (sortConfig.key) {
      result.sort((a, b) => {
        const column = columns.find((col) => col.accessor === sortConfig.key);
        if (!column) return 0;

        const aValue = typeof column.accessor === 'function'
          ? column.accessor(a)
          : a[column.accessor];
        const bValue = typeof column.accessor === 'function'
          ? column.accessor(b)
          : b[column.accessor];

        if (aValue === null || aValue === undefined) return 1;
        if (bValue === null || bValue === undefined) return -1;

        const aStr = String(aValue).toLowerCase();
        const bStr = String(bValue).toLowerCase();

        if (sortConfig.direction === 'asc') {
          return aStr.localeCompare(bStr);
        } else {
          return bStr.localeCompare(aStr);
        }
      });
    }

    return result;
  }, [data, searchTerm, columns, sortConfig]);

  // Calculate pagination
  const totalPages = Math.max(1, Math.ceil(filteredAndSortedData.length / pageSize));
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = filteredAndSortedData.slice(startIndex, endIndex);
  
  // Ensure currentPage is within valid range
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  // Reset to first page when search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const handlePageChange = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 7;
    
    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 4) {
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return <ArrowUpDown size={14} className="text-slate-400" />;
    }
    return sortConfig.direction === 'asc' 
      ? <ArrowUp size={14} className="text-blue-400" />
      : <ArrowDown size={14} className="text-blue-400" />;
  };

  return (
    <div className="space-y-4">
      {/* Top Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
        {showEntries && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Show</span>
            <select
              value={pageSize}
              onChange={handlePageSizeChange}
              className="input-field w-20"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
            <span className="text-sm text-slate-400">entries</span>
          </div>
        )}
        {searchable && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Search:</span>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={searchPlaceholder}
              className="input-field w-48"
            />
          </div>
        )}
      </div>

      {/* Table */}
      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead className="table-header">
            <tr>
              {columns.map((column, index) => {
                const isSortable = column.sortable !== false && column.accessor;
                return (
                  <th
                    key={index}
                    className={`text-left py-3 px-4 ${column.className || ''} ${
                      isSortable ? 'cursor-pointer hover:bg-slate-700 select-none' : ''
                    }`}
                    onClick={() => isSortable && handleSort(column.accessor)}
                  >
                    <div className="flex items-center gap-2">
                      <span>{column.header}</span>
                      {isSortable && getSortIcon(column.accessor)}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="py-8 text-center text-slate-400">
                  Loading...
                </td>
              </tr>
            ) : paginatedData.length > 0 ? (
              paginatedData.map((row, rowIndex) => (
                <tr key={rowIndex} className="table-row">
                  {columns.map((column, colIndex) => {
                    const value = column.accessor
                      ? typeof column.accessor === 'function'
                        ? column.accessor(row)
                        : row[column.accessor]
                      : null;

                    return (
                      <td
                        key={colIndex}
                        className={`py-3 px-4 ${column.cellClassName || ''}`}
                      >
                        {column.cell ? column.cell(row, value) : value}
                      </td>
                    );
                  })}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="py-8 text-center text-slate-400">
                  No data found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {filteredAndSortedData.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-sm text-slate-400">
            Showing {startIndex + 1} to {Math.min(endIndex, filteredAndSortedData.length)} of{' '}
            {filteredAndSortedData.length} entries
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1 rounded bg-slate-700 text-slate-300 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            >
              Previous
            </button>
            {getPageNumbers().map((page, index) => {
              if (page === '...') {
                return (
                  <span key={`ellipsis-${index}`} className="px-2 text-slate-400">
                    ...
                  </span>
                );
              }
              return (
                <button
                  key={page}
                  onClick={() => handlePageChange(page)}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    currentPage === page
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  {page}
                </button>
              );
            })}
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1 rounded bg-slate-700 text-slate-300 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;

