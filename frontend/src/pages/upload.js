import React, { useState } from 'react';
import axios from 'axios';
import Link from 'next/link';

const PDFUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert('Please select a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      setUploading(true);
      setSuccess(false);
      setError(null);

      const response = await axios.post('http://localhost:8000/upload_api', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        setSuccess(true);
        setFile(null);
      }
    } catch (err) {
      setError('An error occurred during the upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-10">
      <h1 className="text-2xl font-semibold text-center text-gray-800 mb-6">Upload PDF</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col items-center">
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div className="text-center">
          <button
            type="submit"
            disabled={uploading}
            className={`px-6 py-2 w-full text-gray-800 font-medium rounded-lg shadow-md bg-blue-400 hover:bg-blue-600 focus:outline-none ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {uploading ? 'Uploading...' : 'Upload PDF'}
          </button>
        </div>
      </form>

      <Link href={"chat"}>Chat</Link>
      {success && <p className="mt-4 text-center text-green-600">File uploaded successfully!</p>}
      {error && <p className="mt-4 text-center text-red-600">{error}</p>}
    </div>
  );
};

export default PDFUpload;
