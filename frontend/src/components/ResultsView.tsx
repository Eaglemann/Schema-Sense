import React, { useState } from 'react';
import { 
  ArrowLeft, 
  Copy, 
  Check, 
  Database, 
  FileText, 
  AlertTriangle,
  BarChart3,
  Hash,
  Percent
} from 'lucide-react';
import { AnalysisResponse } from '../types/api';

interface ResultsViewProps {
  result: AnalysisResponse;
  onReset: () => void;
}

const ResultsView: React.FC<ResultsViewProps> = ({ result, onReset }) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [selectedTab, setSelectedTab] = useState<string>('overview');

  // Put the DDL on the clipboard and show a little confirmation
  const copyToClipboard = async (text: string): Promise<void> => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // flash the "copied" message briefly
    } catch (err) {
      console.error('Failed to copy:', err);
      // clipboard API doesn't work everywhere but oh well
    }
  };

  // Make big numbers easier to read
  const formatNumber = (num: number): string => {
    return num.toLocaleString();
  };

  // Pretty colors for different data types so you can scan them quickly
  const getTypeColor = (mysqlType: string): string => {
    if (mysqlType.includes('INT') || mysqlType.includes('DECIMAL')) {
      return 'bg-blue-100 text-blue-800'; // numbers = blue
    } else if (mysqlType.includes('VARCHAR') || mysqlType.includes('TEXT')) {
      return 'bg-green-100 text-green-800'; // text = green
    } else if (mysqlType.includes('DATE') || mysqlType.includes('TIME')) {
      return 'bg-purple-100 text-purple-800'; // dates = purple
    } else if (mysqlType.includes('BOOLEAN')) {
      return 'bg-orange-100 text-orange-800'; // true/false = orange
    }
    return 'bg-gray-100 text-gray-800'; // everything else = boring gray
  };

  // Traffic light system for missing data - red means you have problems
  const getSeverityColor = (percentage: number): string => {
    if (percentage > 50) return 'text-red-600';    // yikes, mostly empty
    if (percentage > 20) return 'text-orange-600'; // getting concerning
    if (percentage > 5) return 'text-yellow-600';  // a bit spotty
    return 'text-green-600';                       // looking good
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={onReset}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Schema Analysis Complete
                </h1>
                <p className="text-gray-600">
                  {result.file_info.name} • {formatNumber(result.file_info.rows)} rows • {result.file_info.columns} columns
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <span>Separator: "{result.file_info.separator}"</span>
              <span>•</span>
              <span>Encoding: {result.file_info.encoding}</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'overview', name: 'Overview', icon: BarChart3 },
                { id: 'ddl', name: 'DDL Statement', icon: Database },
                { id: 'columns', name: 'Column Details', icon: FileText },
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setSelectedTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      selectedTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === 'overview' && (
              <div className="space-y-6">
                {/* Summary Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center">
                      <Hash className="w-5 h-5 text-blue-600 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-blue-900">Total Columns</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {result.summary.total_columns}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-4">
                    <div className="flex items-center">
                      <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-orange-900">Columns with Nulls</p>
                        <p className="text-2xl font-bold text-orange-600">
                          {result.summary.columns_with_nulls}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="flex items-center">
                      <Percent className="w-5 h-5 text-green-600 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-green-900">Avg Null Rate</p>
                        <p className="text-2xl font-bold text-green-600">
                          {result.summary.avg_null_percentage}%
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <div className="flex items-center">
                      <BarChart3 className="w-5 h-5 text-purple-600 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-purple-900">Recommendations</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {result.summary.total_recommendations}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Type Distribution */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Type Distribution</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {Object.entries(
                      result.columns.reduce((acc: Record<string, number>, col) => {
                        const type = col.mysql_type.split('(')[0];
                        acc[type] = (acc[type] || 0) + 1;
                        return acc;
                      }, {})
                    ).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                        <span className="text-sm font-medium text-gray-700">{type}</span>
                        <span className="text-sm font-bold text-gray-900">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* DDL Tab */}
            {selectedTab === 'ddl' && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">MySQL CREATE TABLE Statement</h3>
                  <button
                    onClick={() => copyToClipboard(result.ddl)}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    <span>{copied ? 'Copied!' : 'Copy DDL'}</span>
                  </button>
                </div>
                <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
                    {result.ddl}
                  </pre>
                </div>
              </div>
            )}

            {/* Columns Tab */}
            {selectedTab === 'columns' && (
              <div className="space-y-6">
                {result.columns.map((column, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <h4 className="text-lg font-semibold text-gray-900 font-mono">
                          {column.name}
                        </h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(column.mysql_type)}`}>
                          {column.mysql_type}
                        </span>
                      </div>
                      <div className="flex space-x-4 text-sm text-gray-500">
                        <span>Unique: {formatNumber(column.unique_count)}</span>
                        <span className={getSeverityColor(column.null_percentage)}>
                          Nulls: {column.null_count} ({column.null_percentage}%)
                        </span>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="bg-white rounded-lg p-4 mb-4">
                      <p className="text-gray-800">{column.description}</p>
                    </div>

                    {/* Sample Values */}
                    {column.sample_values.length > 0 && (
                      <div className="mb-4">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Sample Values</h5>
                        <div className="flex flex-wrap gap-2">
                          {column.sample_values.map((value, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-mono"
                            >
                              {value}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Cleaning Recommendations */}
                    {column.cleaning_recommendations.length > 0 && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <h5 className="text-sm font-medium text-yellow-800 mb-2 flex items-center">
                          <AlertTriangle className="w-4 h-4 mr-1" />
                          Data Quality Recommendations
                        </h5>
                        <ul className="list-disc list-inside space-y-1">
                          {column.cleaning_recommendations.map((rec, idx) => (
                            <li key={idx} className="text-sm text-yellow-700">
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsView;