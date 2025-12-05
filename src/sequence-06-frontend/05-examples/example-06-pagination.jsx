// Pagination
import React, { useState } from 'react';

export default function Pagination({ totalCount, pageSize = 10, onPageChange }) {
  const [page, setPage] = useState(1);
  const totalPages = Math.ceil(totalCount / pageSize);
  
  const change = (newPage) => {
    setPage(newPage);
    onPageChange(newPage);
  };
  
  return (
    <div>
      <button disabled={page === 1} onClick={() => change(page - 1)}>Prev</button>
      <span>Page {page}/{totalPages}</span>
      <button disabled={page >= totalPages} onClick={() => change(page + 1)}>Next</button>
    </div>
  );
}
