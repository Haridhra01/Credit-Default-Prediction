import { useEffect, useState } from 'react'
import './App.css'
import Login from './components/Login'
import Register from './components/Register'

function App() {
  const [authenticated, setAuthenticated] = useState(
    Boolean(localStorage.getItem('access_token'))
  )
  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setAuthenticated(false)
  }
  const [showRegister, setShowRegister] = useState(false)
  const [records, setRecords] = useState([])
  const [selectedRow, setSelectedRow] = useState(null)

  const [datasetInfo, setDatasetInfo] = useState({
    name: 'Credit Card Clients',
    records: 0,
    modelFeatures: 0,
    model: 'XGBoost',
  })

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [currentPage, setCurrentPage] = useState(1)
  const [pageInput, setPageInput] = useState('1')
  const recordsPerPage = 10

  const [prediction, setPrediction] = useState(null)
  const [predictionLoading, setPredictionLoading] = useState(false)
  const [predictionError, setPredictionError] = useState('')

  const [localExplanation, setLocalExplanation] = useState(null)
  const [localLoading, setLocalLoading] = useState(false)
  const [localError, setLocalError] = useState('')

  const [globalExplanation, setGlobalExplanation] = useState(null)
  const [globalLoading, setGlobalLoading] = useState(true)
  const [globalError, setGlobalError] = useState('')

  const [modelPerformance, setModelPerformance] = useState(null)
  const [performanceLoading, setPerformanceLoading] = useState(true)
  const [performanceError, setPerformanceError] = useState('')

  // --------------------------------------------------
  // Dataset Management state
  // --------------------------------------------------

  const [datasetFile, setDatasetFile] = useState(null)
  const [headerRow, setHeaderRow] = useState('')
  const [uploadLoading, setUploadLoading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [uploadMessage, setUploadMessage] = useState('')

  const [profileLoading, setProfileLoading] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [datasetProfile, setDatasetProfile] = useState(null)

  // --------------------------------------------------
  // Dataset Preparation state
  // --------------------------------------------------

  const [targetColumn, setTargetColumn] = useState(
    'default payment next month'
  )

  const [prepareLoading, setPrepareLoading] = useState(false)
  const [prepareError, setPrepareError] = useState('')
  const [datasetPreparation, setDatasetPreparation] =
    useState(null)

  // --------------------------------------------------
  // Preprocessing Analysis state
  // --------------------------------------------------

  const [preprocessLoading, setPreprocessLoading] =
    useState(false)

  const [preprocessError, setPreprocessError] =
    useState('')

  const [preprocessingAnalysis, setPreprocessingAnalysis] =
    useState(null)

  const [applyPreprocessLoading, setApplyPreprocessLoading] = useState(false)
  const [applyPreprocessError, setApplyPreprocessError] = useState('')
  const [preprocessingResult, setPreprocessingResult] = useState(null)

  const processedFilename =
    'default_of_credit_card_clients_processed.csv'

  const apiBaseUrl = 'http://127.0.0.1:8000'

  // --------------------------------------------------
  // Total number of pages
  // --------------------------------------------------

  const totalPages = datasetInfo.records
    ? Math.ceil(
        datasetInfo.records / recordsPerPage
      )
    : 0

  // --------------------------------------------------
  // Keep page input synchronized with current page
  // --------------------------------------------------

  useEffect(() => {

    setPageInput(String(currentPage))
  }, [currentPage])

  // --------------------------------------------------
  // Load customer records for current page
  // --------------------------------------------------

  useEffect(() => {
    const loadRecords = async () => {
      try {
        setLoading(true)
        setError('')
        setSelectedRow(null)

        const offset =
          (currentPage - 1) * recordsPerPage

        const response = await fetch(
          `${apiBaseUrl}/datasets/rows?processed_filename=${encodeURIComponent(
            processedFilename
          )}&offset=${offset}&limit=${recordsPerPage}`
        )

        if (!response.ok) {
          throw new Error(
            `Failed to load records: ${response.status}`
          )
        }

        const data = await response.json()


        setRecords(data.rows || [])

        setDatasetInfo((previous) => ({
          ...previous,
          records: data.total_rows || 0,
        }))

        if (
          data.rows &&
          data.rows.length > 0
        ) {
          setSelectedRow(data.rows[0])
        }
      } catch (err) {
        console.error(
          'Error loading dataset records:',
          err
        )

        setError(
          'Unable to load customer records.'
        )
      } finally {
        setLoading(false)
      }
    }

    loadRecords()
  }, [currentPage])

  // --------------------------------------------------
  // Get prediction whenever selected customer changes
  // --------------------------------------------------

  useEffect(() => {
    const getPrediction = async () => {
      if (!selectedRow) {
        return
      }

      try {
        setPredictionLoading(true)
        setPredictionError('')
        setPrediction(null)

        const response = await fetch(
          `${apiBaseUrl}/prediction?processed_filename=${encodeURIComponent(
            processedFilename
          )}&row_index=${selectedRow.row_index}`,
          {
            method: 'POST',
          }
        )

        if (!response.ok) {
          throw new Error(
            `Prediction failed: ${response.status}`
          )
        }

        const data = await response.json()


        setPrediction(data)
      } catch (err) {
        console.error(
          'Error getting prediction:',
          err
        )

        setPredictionError(
          'Unable to generate prediction.'
        )
      } finally {
        setPredictionLoading(false)
      }
    }

    getPrediction()
  }, [selectedRow])

  // --------------------------------------------------
  // Get local SHAP explanation whenever selected
  // customer changes
  // --------------------------------------------------

  useEffect(() => {
    const getLocalExplanation = async () => {
      if (!selectedRow) {
        return
      }

      try {
        setLocalLoading(true)

        setLocalError('')
        setLocalExplanation(null)

        const response = await fetch(
          `${apiBaseUrl}/xai/local?processed_filename=${encodeURIComponent(
            processedFilename
          )}&row_index=${selectedRow.row_index}`
        )

        if (!response.ok) {
          throw new Error(
            `Local explanation failed: ${response.status}`
          )
        }

        const data = await response.json()

        setLocalExplanation(data)
      } catch (err) {
        console.error(
          'Error getting local explanation:',
          err
        )

        setLocalError(
          'Unable to load local explanation.'
        )
      } finally {
        setLocalLoading(false)
      }
    }


    getLocalExplanation()
  }, [selectedRow])

  // --------------------------------------------------
  // Get model performance
  // --------------------------------------------------
  useEffect(() => {
    const getModelPerformance = async () => {
      try {
        setPerformanceLoading(true)
        setPerformanceError('')

        const response = await fetch(
          `${apiBaseUrl}/prediction/performance?processed_filename=${encodeURIComponent(
            processedFilename
          )}`
        )

        if (!response.ok) {
          throw new Error(
            `Model performance failed: ${response.status}`
          )
        }

        const data = await response.json()
        setModelPerformance(data)
      } catch (err) {
        console.error(
          'Error getting model performance:',
          err
        )
        setPerformanceError(
          'Unable to load model performance.'
        )
      } finally {
        setPerformanceLoading(false)
      }
    }

    getModelPerformance()
  }, [])

  // --------------------------------------------------
  // Get global SHAP explanation
  // --------------------------------------------------

  useEffect(() => {
    const getGlobalExplanation = async () => {
      try {
        setGlobalLoading(true)
        setGlobalError('')
        setGlobalExplanation(null)

        const response = await fetch(
          `${apiBaseUrl}/xai/global?processed_filename=${encodeURIComponent(
            processedFilename
          )}`
        )

        if (!response.ok) {
          throw new Error(
            `Global explanation failed: ${response.status}`
          )
        }

        const data = await response.json()

        setGlobalExplanation(data)


        setDatasetInfo((previous) => ({
          ...previous,
          modelFeatures:
            data.feature_count || 0,
          model: data.model
            ? data.model.toUpperCase()
            : previous.model,
        }))
      } catch (err) {
        console.error(
          'Error getting global explanation:',
          err
        )

        setGlobalError(
          'Unable to load global feature importance.'
        )
      } finally {
        setGlobalLoading(false)
      }
    }

    getGlobalExplanation()
  }, [])

  // --------------------------------------------------
  // Handle dataset file selection
  // --------------------------------------------------

  const handleDatasetFileChange = (event) => {
    const file =

      event.target.files?.[0] || null

    setDatasetFile(file)

    setUploadError('')
    setUploadMessage('')
    setProfileError('')
    setDatasetProfile(null)

    setPrepareError('')
    setDatasetPreparation(null)

    setPreprocessError('')
    setPreprocessingAnalysis(null)
  }

  // --------------------------------------------------
  // Load dataset profile
  // --------------------------------------------------

  const loadDatasetProfile = async (filename) => {
    try {
      setProfileLoading(true)
      setProfileError('')

      const params = new URLSearchParams()

      params.set(
        'filename',
        filename
      )


      if (headerRow.trim() !== '') {
        params.set(
          'header_row',
          headerRow.trim()
        )
      }

      const response = await fetch(
        `${apiBaseUrl}/datasets/profile?${params.toString()}`
      )

      if (!response.ok) {
        throw new Error(
          `Profile request failed: ${response.status}`
        )
      }

      const data =
        await response.json()

      setDatasetProfile(data)
    } catch (err) {
      console.error(
        'Error loading dataset profile:',
        err
      )

      setProfileError(
        'Unable to load dataset profile.'
      )

    } finally {
      setProfileLoading(false)
    }
  }

  // --------------------------------------------------
  // Upload dataset
  // --------------------------------------------------

  const handleDatasetUpload = async () => {
    if (!datasetFile) {
      setUploadError(
        'Please select a dataset file first.'
      )
      return
    }

    try {
      setUploadLoading(true)

      setUploadError('')
      setUploadMessage('')

      setDatasetProfile(null)
      setProfileError('')

      setPrepareError('')
      setDatasetPreparation(null)

      setPreprocessError('')
      setPreprocessingAnalysis(null)


      const formData =
        new FormData()

      formData.append(
        'file',
        datasetFile
      )

      const response =
        await fetch(
          `${apiBaseUrl}/datasets/upload`,
          {
            method: 'POST',
            body: formData,
          }
        )

      if (!response.ok) {
        throw new Error(
          `Upload failed: ${response.status}`
        )
      }

      await response.json()

      setUploadMessage(
        'Dataset uploaded successfully.'
      )

      await loadDatasetProfile(

        datasetFile.name
      )
    } catch (err) {
      console.error(
        'Error uploading dataset:',
        err
      )

      setUploadError(
        'Unable to upload dataset.'
      )
    } finally {
      setUploadLoading(false)
    }
  }

  // --------------------------------------------------
  // Prepare uploaded dataset
  // --------------------------------------------------

  const handleDatasetPrepare = async () => {
    if (!datasetFile) {
      setPrepareError(
        'Please upload a dataset first.'
      )
      return
    }

    if (!targetColumn.trim()) {
      setPrepareError(
        'Please enter the target column.'

      )
      return
    }

    try {
      setPrepareLoading(true)
      setPrepareError('')
      setDatasetPreparation(null)

      const requestBody = {
        filename:
          datasetFile.name,

        target_column:
          targetColumn.trim(),

        header_row:
          headerRow.trim() !== ''
            ? Number(
                headerRow.trim()
              )
            : null,
      }

      const response =
        await fetch(
          `${apiBaseUrl}/datasets/prepare`,
          {
            method: 'POST',

            headers: {

              'Content-Type':
                'application/json',
            },

            body:
              JSON.stringify(
                requestBody
              ),
          }
        )

      if (!response.ok) {
        const errorData =
          await response
            .json()
            .catch(
              () => null
            )

        throw new Error(
          errorData?.detail ||
            `Preparation failed: ${response.status}`
        )
      }

      const data =
        await response.json()

      setDatasetPreparation(data)

      setDatasetInfo(

        (previous) => ({
          ...previous,

          name:
            data.filename ||
            previous.name,

          records:
            data.total_rows ||
            previous.records,
        })
      )
    } catch (err) {
      console.error(
        'Error preparing dataset:',
        err
      )

      setPrepareError(
        err.message ||
          'Unable to prepare dataset.'
      )
    } finally {
      setPrepareLoading(false)
    }
  }

  // --------------------------------------------------
  // Analyze preprocessing requirements
  // --------------------------------------------------
  const handlePreprocessAnalysis =
    async () => {
      if (!datasetFile) {
        setPreprocessError(
          'Please upload a dataset first.'
        )
        return
      }

      if (!targetColumn.trim()) {
        setPreprocessError(
          'Please enter the target column first.'
        )
        return
      }

      try {
        setPreprocessLoading(true)
        setPreprocessError('')
        setPreprocessingAnalysis(null)

        const requestBody = {
          filename:
            datasetFile.name,

          target_column:
            targetColumn.trim(),

          header_row:
            headerRow.trim() !== ''
              ? Number(

                  headerRow.trim()
                )
              : null,
        }

        const response =
          await fetch(
            `${apiBaseUrl}/datasets/preprocess`,
            {
              method: 'POST',

              headers: {
                'Content-Type':
                  'application/json',
              },

              body:
                JSON.stringify(
                  requestBody
                ),
            }
          )

        if (!response.ok) {
          const errorData =
            await response
              .json()
              .catch(
                () => null
              )


          throw new Error(
            errorData?.detail ||
              `Preprocessing analysis failed: ${response.status}`
          )
        }

        const data =
          await response.json()

        setPreprocessingAnalysis(
          data
        )
      } catch (err) {
        console.error(
          'Error analyzing preprocessing:',
          err
        )

        setPreprocessError(
          err.message ||
            'Unable to analyze preprocessing requirements.'
        )
      } finally {
        setPreprocessLoading(
          false
        )
      }
    }

  // --------------------------------------------------
  // Handle customer selection
  // --------------------------------------------------

  const handleApplyPreprocessing = async () => {
    if (!datasetFile) {
      setApplyPreprocessError('Please upload a dataset first.')
      return
    }
    if (!targetColumn.trim()) {
      setApplyPreprocessError('Please enter the target column first.')
      return
    }
    try {
      setApplyPreprocessLoading(true)
      setApplyPreprocessError('')
      setPreprocessingResult(null)
      const requestBody = {
        filename: datasetFile.name,
        target_column: targetColumn.trim(),
        header_row: headerRow.trim() !== '' ? Number(headerRow.trim()) : null,
      }
      const response = await fetch(`${apiBaseUrl}/datasets/preprocess/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      })
      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || `Preprocessing failed: ${response.status}`)
      }
      const data = await response.json()
      setPreprocessingResult(data)
    } catch (err) {
      console.error('Error applying preprocessing:', err)
      setApplyPreprocessError(err.message || 'Unable to apply dataset preprocessing.')
    } finally {
      setApplyPreprocessLoading(false)
    }
  }

  const handleCustomerChange = (
    event
  ) => {
    const rowIndex =
      Number(
        event.target.value
      )

    const selectedRecord =
      records.find(
        (record) =>
          record.row_index ===
          rowIndex
      )

    setSelectedRow(
      selectedRecord || null
    )
  }

  // --------------------------------------------------
  // Handle previous page
  // --------------------------------------------------

  const handlePreviousPage =
    () => {
      if (currentPage > 1) {
        setCurrentPage(
          (previous) =>

            previous - 1
        )
      }
    }

  // --------------------------------------------------
  // Handle next page
  // --------------------------------------------------

  const handleNextPage = () => {
    if (
      currentPage <
      totalPages
    ) {
      setCurrentPage(
        (previous) =>
          previous + 1
      )
    }
  }

  // --------------------------------------------------
  // Handle direct page navigation
  // --------------------------------------------------

  const handlePageInputChange =
    (event) => {
      setPageInput(
        event.target.value
      )
    }


  const handleGoToPage = () => {
    const requestedPage =
      Number(pageInput)

    if (
      !Number.isInteger(
        requestedPage
      )
    ) {
      setPageInput(
        String(currentPage)
      )
      return
    }

    if (requestedPage < 1) {
      setCurrentPage(1)
      return
    }

    if (
      requestedPage >
      totalPages
    ) {
      setCurrentPage(
        totalPages
      )
      return
    }


    setCurrentPage(
      requestedPage
    )
  }

  // --------------------------------------------------
  // Allow Enter key for direct page navigation
  // --------------------------------------------------

  const handlePageInputKeyDown =
    (event) => {
      if (
        event.key === 'Enter'
      ) {
        handleGoToPage()
      }
    }

  // --------------------------------------------------
  // Default probability
  // --------------------------------------------------

  const probability =
    prediction
      ? prediction.default_probability *
        100
      : 0

  // --------------------------------------------------
  // Top 5 features increasing prediction
  // --------------------------------------------------
  const businessFeatureNames = {
    PAY_0: 'Most Recent Repayment Status',
    PAY_2: 'Previous Repayment Status',
    PAY_3: 'Earlier Repayment Status',
    PAY_4: 'Older Repayment Status',
    PAY_5: 'Earlier Repayment Status',
    PAY_6: 'Oldest Repayment Status',
    LIMIT_BAL: 'Credit Limit Assigned',
    BILL_AMT1: 'Most Recent Billed Amount',
    BILL_AMT2: 'Previous Billed Amount',
    BILL_AMT3: 'Earlier Billed Amount',
    BILL_AMT4: 'Older Billed Amount',
    BILL_AMT5: 'Earlier Billed Amount',
    BILL_AMT6: 'Oldest Billed Amount',
    PAY_AMT1: 'Most Recent Payment Amount',
    PAY_AMT2: 'Previous Payment Amount',
    PAY_AMT3: 'Earlier Payment Amount',
    PAY_AMT4: 'Older Payment Amount',
    PAY_AMT5: 'Earlier Payment Amount',
    PAY_AMT6: 'Oldest Payment Amount',
    AGE: 'Customer Age',
    SEX: 'Customer Gender',
    EDUCATION: 'Education Level',
    MARRIAGE: 'Marital Status'
  }

  const increasingFeatures =
    localExplanation
      ? localExplanation.contributions
          .filter(
            (item) =>
              item.direction ===
              'increases'
          )
          .sort(
            (a, b) =>
              Math.abs(
                b.shap_value
              ) -
              Math.abs(
                a.shap_value
              )
          )
          .slice(0, 5)
      : []

  // --------------------------------------------------
  // Top 5 features decreasing prediction
  // --------------------------------------------------

  const decreasingFeatures =
    localExplanation
      ? localExplanation.contributions
          .filter(
            (item) =>
              item.direction ===

              'decreases'
          )
          .sort(
            (a, b) =>
              Math.abs(
                b.shap_value
              ) -
              Math.abs(
                a.shap_value
              )
          )
          .slice(0, 5)
      : []

  // --------------------------------------------------
  // Largest local SHAP value for scaling
  // --------------------------------------------------

  const maxShapValue =
    localExplanation
      ? Math.max(
          ...localExplanation.contributions.map(
            (item) =>
              Math.abs(
                item.shap_value
              )
          ),
          0.0001
        )
      : 1


  // --------------------------------------------------
  // Top global SHAP features
  // --------------------------------------------------

  const globalFeatures =
    globalExplanation
      ? globalExplanation.feature_importance.slice(
          0,
          5
        )
      : []

  // --------------------------------------------------
  // Largest global SHAP value for scaling
  // --------------------------------------------------

  const maxGlobalShapValue =
    globalFeatures.length
      ? Math.max(
          ...globalFeatures.map(
            (item) =>
              item.mean_absolute_shap
          ),
          0.0001
        )
      : 1

  // --------------------------------------------------
  // Business Insight factors
  // --------------------------------------------------
  const topIncreasingFeatures =
    increasingFeatures
      .slice(0, 3)
      .map(
        (item) =>
          item.feature
      )

  const topDecreasingFeatures =
    decreasingFeatures
      .slice(0, 3)
      .map(
        (item) =>
          item.feature
      )

  const topGlobalFeature =
    globalExplanation
      ?.feature_importance[0]
      ?.feature

  // --------------------------------------------------
  // Dataset profile values
  // --------------------------------------------------

  const profileBasic =
    datasetProfile?.basic_profile

  const profileQuality =
    datasetProfile?.data_quality

  if (!authenticated) {
    if (showRegister) {
      return (
        <Register
          onBackToLogin={() => setShowRegister(false)}
        />
      )
    }

    return (
      <Login
        onLogin={() => setAuthenticated(true)}
        onRegister={() => setShowRegister(true)}
      />
    )
  }

  return (
    <div className="app">

      {/* Top Navigation */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            E
          </div>
          <div>
            <h1>
              ExplainBI
            </h1>
            <p>
              Explainable Business Intelligence
            </p>
          </div>
        </div>

        <div className="topbar-actions">
          <div className="status">
            <span className="status-dot"></span>
            Model Ready
          </div>

          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="dashboard">

        {/* Page Heading */}
        <section className="page-heading">

          <div>

            <span className="eyebrow">
              EXPLAINABLE ANALYTICS
            </span>

            <h2>
              Business Intelligence Dashboard
            </h2>

            <p className="description">
              Understand customer predictions through transparent
              machine learning explanations.
            </p>

          </div>

        </section>

        {/* ==================================================
            DATASET MANAGEMENT
        ================================================== */}

        <section className="panel dataset-management-panel">

          <div className="panel-header">

            <div>

              <span className="panel-kicker">
                DATASET MANAGEMENT
              </span>

              <h3>
                Upload &amp; Profile Dataset
              </h3>

            </div>

            <span className="panel-note">
              Dataset preparation
            </span>

          </div>

          <div className="dataset-upload-area">

            <div className="dataset-file-field">

              <label htmlFor="dataset-file">
                Dataset File

              </label>

              <input
                id="dataset-file"
                type="file"
                accept=".csv,.xls,.xlsx"
                onChange={
                  handleDatasetFileChange
                }
                disabled={
                  uploadLoading
                }
              />

            </div>

            <div className="dataset-header-field">

              <label htmlFor="header-row">
                Header Row
              </label>

              <input
                id="header-row"
                type="number"
                min="0"
                placeholder="Auto detect"
                value={headerRow}
                onChange={(event) =>
                  setHeaderRow(
                    event.target.value

                  )
                }
                disabled={
                  uploadLoading
                }
              />

              <small>
                Optional. Leave empty for automatic
                Excel header detection.
              </small>

            </div>

            <button
              type="button"
              className="dataset-upload-button"
              onClick={
                handleDatasetUpload
              }
              disabled={
                uploadLoading ||
                !datasetFile
              }
            >
              {uploadLoading
                ? 'Uploading...'
                : 'Upload Dataset'}
            </button>

          </div>


          {datasetFile && (
            <div className="dataset-selected-file">

              Selected file:{' '}

              <strong>
                {datasetFile.name}
              </strong>

            </div>
          )}

          {uploadMessage && (
            <div className="dataset-success-message">
              {uploadMessage}
            </div>
          )}

          {uploadError && (
            <div className="dataset-error-message">
              {uploadError}
            </div>
          )}

          {profileLoading && (
            <div className="dataset-profile-loading">
              Loading dataset profile...
            </div>
          )}


          {profileError && (
            <div className="dataset-error-message">
              {profileError}
            </div>
          )}

          {profileBasic && (
            <div className="dataset-profile-section">

              <div className="dataset-profile-heading">

                <div>

                  <span className="panel-kicker">
                    DATASET PROFILE
                  </span>

                  <h3>
                    {datasetFile?.name ||
                      'Uploaded Dataset'}
                  </h3>

                </div>

              </div>

              <div className="dataset-profile-cards">

                <div className="dataset-profile-card">

                  <span>

                    Rows
                  </span>

                  <strong>
                    {profileBasic.total_rows?.toLocaleString() ||
                      '--'}
                  </strong>

                </div>

                <div className="dataset-profile-card">

                  <span>
                    Columns
                  </span>

                  <strong>
                    {profileBasic.total_columns ||
                      '--'}
                  </strong>

                </div>

                <div className="dataset-profile-card">

                  <span>
                    Missing Values
                  </span>

                  <strong>
                    {profileQuality?.total_missing_values ??

                      '--'}
                  </strong>

                </div>

                <div className="dataset-profile-card">

                  <span>
                    Duplicate Rows
                  </span>

                  <strong>
                    {profileQuality?.duplicate_rows ??
                      '--'}
                  </strong>

                </div>

              </div>

              {datasetProfile.preview &&
                datasetProfile.preview.length >
                  0 && (

                  <div className="dataset-preview-section">

                    <div className="dataset-profile-heading">

                      <div>

                        <span className="panel-kicker">

                          DATA PREVIEW
                        </span>

                        <h3>
                          Preview Records
                        </h3>

                      </div>

                    </div>

                    <div className="dataset-table-wrapper">

                      <table className="dataset-table">

                        <thead>

                          <tr>

                            {Object.keys(
                              datasetProfile.preview[0]
                            ).map(
                              (column) => (
                                <th
                                  key={
                                    column
                                  }
                                >
                                  {column}
                                </th>
                              )

                            )}

                          </tr>

                        </thead>

                        <tbody>

                          {datasetProfile.preview
                            .slice(0, 5)
                            .map(
                              (
                                row,
                                rowIndex
                              ) => (

                                <tr
                                  key={
                                    rowIndex
                                  }
                                >

                                  {Object.keys(
                                    datasetProfile.preview[0]
                                  ).map(
                                    (
                                      column
                                    ) => (

                                      <td
                                        key={

                                          column
                                        }
                                      >
                                        {String(
                                          row[
                                            column
                                          ] ??
                                            ''
                                        )}
                                      </td>

                                    )
                                  )}

                                </tr>

                              )
                            )}

                        </tbody>

                      </table>

                    </div>

                  </div>

                )}

            </div>
          )}

          {/* ==================================================
              DATASET PREPARATION
          ================================================== */}

          <div
            className="dataset-profile-section"
            style={{
              marginTop: '24px',
            }}
          >

            <div className="dataset-profile-heading">

              <div>

                <span className="panel-kicker">
                  DATASET PREPARATION
                </span>

                <h3>
                  Prepare Dataset for Machine Learning
                </h3>

              </div>

              <span className="panel-note">
                Target &amp; problem type
              </span>

            </div>

            <div
              className="dataset-upload-area"
              style={{
                marginTop: '16px',
              }}
            >

              <div className="dataset-file-field">

                <label htmlFor="target-column">
                  Target Column
                </label>

                <input
                  id="target-column"
                  type="text"
                  value={
                    targetColumn
                  }
                  onChange={(event) =>
                    setTargetColumn(
                      event.target.value
                    )
                  }
                  placeholder="Enter target column"
                  disabled={
                    prepareLoading ||
                    preprocessLoading
                  }
                />


                <small>
                  Example: default payment next month
                </small>

              </div>

              <button
                type="button"
                className="dataset-upload-button"
                onClick={
                  handleDatasetPrepare
                }
                disabled={
                  prepareLoading ||
                  !datasetFile
                }
              >
                {prepareLoading
                  ? 'Preparing...'
                  : 'Prepare Dataset'}
              </button>

            </div>

            {prepareError && (
              <div className="dataset-error-message">
                {prepareError}
              </div>
            )}

            {datasetPreparation && (
              <div
                className="dataset-profile-cards"
                style={{
                  marginTop: '18px',
                }}
              >

                <div className="dataset-profile-card">

                  <span>
                    Target Column
                  </span>

                  <strong
                    style={{
                      fontSize:
                        '14px',
                      wordBreak:
                        'break-word',
                    }}
                  >
                    {
                      datasetPreparation.target_column
                    }
                  </strong>

                </div>

                <div className="dataset-profile-card">


                  <span>
                    Problem Type
                  </span>

                  <strong>
                    {
                      datasetPreparation.problem_type
                    }
                  </strong>

                </div>

                <div className="dataset-profile-card">

                  <span>
                    Rows
                  </span>

                  <strong>
                    {datasetPreparation.total_rows?.toLocaleString() ||
                      '--'}
                  </strong>

                </div>

                <div className="dataset-profile-card">

                  <span>
                    Columns
                  </span>


                  <strong>
                    {
                      datasetPreparation.total_columns ??
                      '--'
                    }
                  </strong>

                </div>

                <div className="dataset-profile-card">

                  <span>
                    Feature Count
                  </span>

                  <strong>
                    {
                      datasetPreparation.feature_count ??
                      '--'
                    }
                  </strong>

                </div>

                <div className="dataset-profile-card">

                  <span>
                    Target Classes
                  </span>

                  <strong

                    style={{
                      fontSize:
                        '14px',
                    }}
                  >
                    {datasetPreparation.target_classes?.join(
                      ', '
                    ) ||
                      '--'}
                  </strong>

                </div>

              </div>
            )}

          </div>

          {/* ==================================================
              PREPROCESSING ANALYSIS
          ================================================== */}
          <div
            className="dataset-profile-section"
            style={{
              marginTop: '24px',
            }}
          >

            <div className="dataset-profile-heading">

              <div>

                <span className="panel-kicker">
                  PREPROCESSING
                </span>

                <h3>
                  Analyze Preprocessing Requirements
                </h3>

              </div>

              <span className="panel-note">
                Data preparation analysis
              </span>

            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent:
                  'space-between',
                gap: '16px',
                marginTop: '16px',
                flexWrap: 'wrap',
              }}
            >

              <p

                style={{
                  margin: 0,
                  fontSize: '13px',
                  color: '#64748b',
                }}
              >
                Check missing values, duplicates,
                feature types, scaling and encoding
                requirements before applying preprocessing.
              </p>

              <button
                type="button"
                className="dataset-upload-button"
                onClick={
                  handlePreprocessAnalysis
                }
                disabled={
                  preprocessLoading ||
                  !datasetFile
                }
              >
                {preprocessLoading
                  ? 'Analyzing...'
                  : 'Analyze Preprocessing'}
              </button>

            </div>

            {preprocessError && (
              <div

                className="dataset-error-message"
                style={{
                  marginTop: '14px',
                }}
              >
                {preprocessError}
              </div>
            )}

            {preprocessingAnalysis && (
              <div
                style={{
                  marginTop: '18px',
                }}
              >

                <div className="dataset-profile-cards">

                  <div className="dataset-profile-card">

                    <span>
                      Problem Type
                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.problem_type
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Rows
                    </span>

                    <strong>
                      {preprocessingAnalysis.total_rows?.toLocaleString() ||
                        '--'}
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Columns
                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.total_columns ??
                        '--'
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Feature Count
                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.feature_count ??
                        '--'
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Missing Values
                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.missing_values ??
                        '--'
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>

                      Duplicate Rows
                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.duplicate_rows ??
                        '--'
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Target Missing Values
                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.target_missing_values ??
                        '--'
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Target Unique Values

                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.target_unique_values ??
                        '--'
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Scaling Required
                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.scaling_required
                          ? 'Yes'
                          : 'No'
                      }
                    </strong>

                  </div>

                  <div className="dataset-profile-card">

                    <span>
                      Encoding Required

                    </span>

                    <strong>
                      {
                        preprocessingAnalysis.encoding_required
                          ? 'Yes'
                          : 'No'
                      }
                    </strong>

                  </div>

                </div>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns:
                      'repeat(auto-fit, minmax(240px, 1fr))',
                    gap: '16px',
                    marginTop: '16px',
                  }}
                >

                  <div
                    className="dataset-profile-card"
                    style={{
                      minHeight:
                        '100px',
                    }}
                  >

                    <span>
                      Numerical Features
                    </span>

                    <strong
                      style={{
                        fontSize:
                          '12px',
                        lineHeight:
                          '1.6',
                        wordBreak:
                          'break-word',
                      }}
                    >
                      {preprocessingAnalysis.numerical_features?.length
                        ? preprocessingAnalysis.numerical_features.join(
                            ', '
                          )
                        : 'None'}
                    </strong>

                  </div>

                  <div
                    className="dataset-profile-card"
                    style={{
                      minHeight:
                        '100px',
                    }}
                  >

                    <span>
                      Categorical Features
                    </span>

                    <strong
                      style={{
                        fontSize:
                          '12px',
                        lineHeight:
                          '1.6',
                        wordBreak:
                          'break-word',
                      }}
                    >
                      {preprocessingAnalysis.categorical_features?.length
                        ? preprocessingAnalysis.categorical_features.join(
                            ', '
                          )
                        : 'None'}
                    </strong>

                  </div>

                  <div
                    className="dataset-profile-card"
                    style={{
                      minHeight:
                        '100px',
                    }}
                  >


                    <span>
                      Target Classes
                    </span>

                    <strong
                      style={{
                        fontSize:
                          '12px',
                        lineHeight:
                          '1.6',
                      }}
                    >
                      {preprocessingAnalysis.target_classes?.length
                        ? preprocessingAnalysis.target_classes.join(
                            ', '
                          )
                        : 'None'}
                    </strong>

                  </div>

                </div>

              </div>
            )}

          </div>

        </section>


        {/* Apply Preprocessing */}
        {preprocessingAnalysis && (
          <div style={{ marginTop: '20px', paddingTop: '18px', borderTop: '1px solid #e5e7eb' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
              <div>
                <span className="panel-kicker">APPLY PREPROCESSING</span>
                <p style={{ margin: '6px 0 0', fontSize: '13px', color: '#64748b' }}>
                  Apply the analyzed preprocessing steps and create the processed dataset.
                </p>
              </div>
              <button type="button" className="dataset-upload-button" onClick={handleApplyPreprocessing} disabled={applyPreprocessLoading || !datasetFile}>
                {applyPreprocessLoading ? 'Processing...' : 'Apply Preprocessing'}
              </button>
            </div>
            {applyPreprocessError && (
              <div className="dataset-error-message" style={{ marginTop: '14px' }}>{applyPreprocessError}</div>
            )}
            {preprocessingResult && (
              <div style={{ marginTop: '18px' }}>
                <div className="dataset-success-message" style={{ marginBottom: '16px' }}>{preprocessingResult.message}</div>
                <div className="dataset-profile-cards">
                  <div className="dataset-profile-card"><span>Processed File</span><strong style={{ fontSize: '12px', wordBreak: 'break-word' }}>{preprocessingResult.processed_filename}</strong></div>
                  <div className="dataset-profile-card"><span>Original Rows</span><strong>{preprocessingResult.original_rows?.toLocaleString() ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Processed Rows</span><strong>{preprocessingResult.processed_rows?.toLocaleString() ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Original Features</span><strong>{preprocessingResult.original_feature_count ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Processed Features</span><strong>{preprocessingResult.processed_feature_count ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Missing Values Before</span><strong>{preprocessingResult.missing_values_before ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Missing Values After</span><strong>{preprocessingResult.missing_values_after ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Duplicates Removed</span><strong>{preprocessingResult.duplicate_rows_removed ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Target Rows Removed</span><strong>{preprocessingResult.target_missing_rows_removed ?? '--'}</strong></div>
                  <div className="dataset-profile-card"><span>Scaling Applied</span><strong>{preprocessingResult.scaling_applied ? 'Yes' : 'No'}</strong></div>
                  <div className="dataset-profile-card"><span>Encoding Applied</span><strong>{preprocessingResult.encoding_applied ? 'Yes' : 'No'}</strong></div>
                  <div className="dataset-profile-card"><span>Problem Type</span><strong>{preprocessingResult.problem_type}</strong></div>
                </div>
                <div className="dataset-profile-card" style={{ marginTop: '16px', minHeight: '100px' }}>
                  <span>Processed Columns</span>
                  <strong style={{ fontSize: '12px', lineHeight: '1.6', wordBreak: 'break-word' }}>{preprocessingResult.processed_columns?.join(', ') || 'None'}</strong>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Dataset Overview */}
        <section className="overview-grid">

          <div className="stat-card">

            <span className="stat-label">
              Dataset
            </span>

            <strong>
              {datasetInfo.name}
            </strong>

            <small>
              Processed dataset
            </small>

          </div>

          <div className="stat-card">

            <span className="stat-label">
              Records
            </span>

            <strong>
              {datasetInfo.records
                ? datasetInfo.records.toLocaleString()
                : '--'}
            </strong>


            <small>
              Customer records
            </small>

          </div>

          <div className="stat-card">

            <span className="stat-label">
              Model Features
            </span>

            <strong>
              {datasetInfo.modelFeatures ||
                '--'}
            </strong>

            <small>
              Features used by model
            </small>

          </div>

          <div className="stat-card">

            <span className="stat-label">
              Model
            </span>

            <strong>
              {datasetInfo.model}

            </strong>

            <small>
              Classification model
            </small>

          </div>

        </section>

        {/* ML Model & Explainability Status */}
        <section className="panel" style={{ marginTop: '24px' }}>
          <div className="panel-header">
            <div>
              <span className="panel-kicker">
                ML PIPELINE STATUS
              </span>
              <h3>
                Model & Explainability Status
              </h3>
            </div>
            <span className="panel-note">
              Current model state
            </span>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '12px',
              marginTop: '18px',
            }}
          >
            {[
              ['Dataset Preparation', 'Completed'],
              ['Preprocessing', 'Applied'],
              ['Feature Selection', 'SelectKBest'],
              ['Machine Learning Model', 'XGBoost — Trained'],
              ['Model Evaluation', 'Completed'],
              ['Explainability', 'SHAP — Ready'],
            ].map(([label, value]) => (
              <div
                key={label}
                className="dataset-profile-card"
                style={{
                  minHeight: '86px',
                  position: 'relative',
                  paddingLeft: '38px',
                }}
              >
                <span
                  style={{
                    position: 'absolute',
                    left: '14px',
                    top: '18px',
                    fontSize: '16px',
                  }}
                >
                  ✓
                </span>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        {/* Model Performance */}
        <section className="panel" style={{ marginTop: '24px' }}>
          <div className="panel-header">
            <div>
              <span className="panel-kicker">
                MODEL PERFORMANCE
              </span>
              <h3>
                XGBoost Model Evaluation
              </h3>
            </div>
            <span className="panel-note">
              Test-set performance
            </span>
          </div>

          {performanceLoading ? (
            <div className="empty-state">
              <h4>
                Loading model performance...
              </h4>
              <p>
                Calculating evaluation metrics.
              </p>
            </div>
          ) : performanceError ? (
            <div className="empty-state">
              <p>{performanceError}</p>
            </div>
          ) : modelPerformance ? (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '12px',
                marginTop: '18px',
              }}
            >
              {[
                ['Model', modelPerformance.model?.toUpperCase() || '--'],
                ['Training Rows', modelPerformance.training_rows?.toLocaleString() || '--'],
                ['Testing Rows', modelPerformance.testing_rows?.toLocaleString() || '--'],
                ['Accuracy', `${(modelPerformance.accuracy * 100).toFixed(2)}%`],
                ['Precision', `${(modelPerformance.precision * 100).toFixed(2)}%`],
                ['Recall', `${(modelPerformance.recall * 100).toFixed(2)}%`],
                ['F1 Score', `${(modelPerformance.f1_score * 100).toFixed(2)}%`],
                ['ROC-AUC', `${(modelPerformance.roc_auc * 100).toFixed(2)}%`],
                ['Selected Features', modelPerformance.selected_feature_count ?? '--'],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="dataset-profile-card"
                  style={{ minHeight: '86px' }}
                >
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
          ) : null}
        </section>

        {/* Main Content */}
        <section className="content-grid">

          {/* Customer Analysis */}
          <div className="panel">

            <div className="panel-header">

              <div>

                <span className="panel-kicker">
                  CUSTOMER ANALYSIS
                </span>

                <h3>
                  Select Customer Record
                </h3>

              </div>

              <span className="panel-note">

                Individual prediction
              </span>

            </div>

            {/* Customer Selector */}
            <div className="customer-selector">

              <label htmlFor="customer-select">
                Customer Record
              </label>

              <select
                id="customer-select"
                value={
                  selectedRow
                    ? selectedRow.row_index
                    : ''
                }
                onChange={
                  handleCustomerChange
                }
                disabled={
                  loading ||
                  records.length === 0
                }
              >

                {loading ? (

                  <option value="">

                    Loading records...
                  </option>

                ) : (

                  records.map(
                    (record) => (

                      <option
                        key={
                          record.row_index
                        }
                        value={
                          record.row_index
                        }
                      >
                        Customer Record{' '}
                        {record.row_index + 1}
                      </option>

                    )
                  )

                )}

              </select>

            </div>

            {/* Pagination */}
            <div

              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent:
                  'space-between',
                gap: '10px',
                marginTop: '12px',
                marginBottom: '18px',
                flexWrap: 'wrap',
              }}
            >

              <button
                type="button"
                onClick={
                  handlePreviousPage
                }
                disabled={
                  loading ||
                  currentPage <= 1
                }
                style={{
                  padding:
                    '8px 14px',
                  borderRadius:
                    '6px',
                  border:
                    '1px solid #d9e0ea',
                  background:
                    '#ffffff',
                  cursor:

                    loading ||
                    currentPage <=
                      1
                      ? 'not-allowed'
                      : 'pointer',
                  opacity:
                    loading ||
                    currentPage <=
                      1
                      ? 0.5
                      : 1,
                }}
              >
                Previous
              </button>

              <span
                style={{
                  fontSize:
                    '12px',
                  color:
                    '#64748b',
                  whiteSpace:
                    'nowrap',
                }}
              >
                Page {currentPage} of{' '}
                {totalPages || '--'}
              </span>

              <div

                style={{
                  display:
                    'flex',
                  alignItems:
                    'center',
                  gap: '6px',
                }}
              >

                <input
                  type="number"
                  min="1"
                  max={
                    totalPages ||
                    1
                  }
                  value={
                    pageInput
                  }
                  onChange={
                    handlePageInputChange
                  }
                  onKeyDown={
                    handlePageInputKeyDown
                  }
                  disabled={
                    loading ||
                    totalPages ===
                      0
                  }
                  aria-label="Page number"

                  style={{
                    width:
                      '58px',
                    padding:
                      '8px',
                    borderRadius:
                      '6px',
                    border:
                      '1px solid #d9e0ea',
                    fontSize:
                      '12px',
                    boxSizing:
                      'border-box',
                  }}
                />

                <button
                  type="button"
                  onClick={
                    handleGoToPage
                  }
                  disabled={
                    loading ||
                    totalPages ===
                      0
                  }
                  style={{
                    padding:
                      '8px 12px',
                    borderRadius:
                      '6px',

                    border:
                      '1px solid #d9e0ea',
                    background:
                      '#ffffff',
                    cursor:
                      loading ||
                      totalPages ===
                        0
                        ? 'not-allowed'
                        : 'pointer',
                    opacity:
                      loading ||
                      totalPages ===
                        0
                        ? 0.5
                        : 1,
                  }}
                >
                  Go
                </button>

              </div>

              <button
                type="button"
                onClick={
                  handleNextPage
                }
                disabled={
                  loading ||
                  currentPage >=

                    totalPages
                }
                style={{
                  padding:
                    '8px 14px',
                  borderRadius:
                    '6px',
                  border:
                    '1px solid #d9e0ea',
                  background:
                    '#ffffff',
                  cursor:
                    loading ||
                    currentPage >=
                      totalPages
                      ? 'not-allowed'
                      : 'pointer',
                  opacity:
                    loading ||
                    currentPage >=
                      totalPages
                      ? 0.5
                      : 1,
                }}
              >
                Next
              </button>

            </div>

            {/* Dataset Loading Error */}

            {error && (
              <div className="empty-state">

                <div className="empty-icon">
                  !
                </div>

                <h4>
                  Unable to load records
                </h4>

                <p>
                  {error}
                </p>

              </div>
            )}

            {!error &&
              selectedRow && (
                <>

                  {/* Prediction */}
                  <div className="prediction-box">

                    <span className="prediction-label">
                      Prediction
                    </span>

                    {predictionLoading ? (

                      <strong>
                        Analyzing...
                      </strong>

                    ) : prediction ? (

                      <>

                        <strong>
                          {
                            prediction.prediction_label
                          }
                        </strong>

                        <span className="prediction-badge">
                          {
                            prediction.prediction_label
                          }
                        </span>

                      </>

                    ) : (

                      <strong>
                        Pending analysis
                      </strong>

                    )}

                  </div>


                  {/* Default Probability */}
                  <div className="probability-section">

                    <div className="probability-header">

                      <span>
                        Default Probability
                      </span>

                      <strong>
                        {predictionLoading
                          ? '--'
                          : prediction
                            ? `${probability.toFixed(
                                2
                              )}%`
                            : '--'}
                      </strong>

                    </div>

                    <div className="progress-track">

                      <div
                        className="progress-fill"
                        style={{
                          width: `${probability}%`,
                        }}
                      ></div>


                    </div>

                  </div>

                  {/* Prediction Error */}
                  {predictionError && (
                    <div className="empty-state">

                      <div className="empty-icon">
                        !
                      </div>

                      <h4>
                        Prediction unavailable
                      </h4>

                      <p>
                        {predictionError}
                      </p>

                    </div>
                  )}

                  {/* Local Explanation */}
                  <div className="panel-header">

                    <div>

                      <span className="panel-kicker">
                        XAI
                      </span>

                      <h3>
                        Local Explanation
                      </h3>

                    </div>

                    <span className="panel-note">
                      SHAP
                    </span>

                  </div>

                  {localLoading ? (

                    <div className="empty-state">

                      <div className="empty-icon">
                        ✦
                      </div>

                      <h4>
                        Generating explanation...
                      </h4>

                      <p>
                        Calculating the factors
                        influencing this prediction.
                      </p>
                    </div>
                  ) : localError ? (
                    <div className="empty-state">
                      <div className="empty-icon">
                        !
                      </div>
                      <h4>
                        Explanation unavailable
                      </h4>
                      <p>
                        {localError}
                      </p>
                    </div>
                  ) : localExplanation ? (
                    <div className="importance-list">
                      {/* Increasing Factors */}
                      <div>
                        <span className="panel-kicker">
                          INCREASES PREDICTION
                        </span>
                      </div>
                      {increasingFeatures.map(
                        (item) => (

                          <div
                            className="importance-row"
                            key={
                              item.feature
                            }
                          >
                            <span>
                              {businessFeatureNames[item.feature]
                                ? `${businessFeatureNames[item.feature]} (${item.feature})`
                                : item.feature}
                            </span>
                            <div className="importance-track">
                              <div
                                className="importance-fill"
                                style={{
                                  width: `${
                                    (Math.abs(
                                      item.shap_value
                                    ) /
                                      maxShapValue) *
                                    100
                                  }%`,
                                }}
                              ></div>
                            </div>
                            <span>
                              +
                              {item.shap_value.toFixed(
                                3
                              )}
                            </span>

                          </div>

                        )
                      )}

                      {/* Decreasing Factors */}
                      <div
                        style={{
                          marginTop:
                            '20px',
                        }}
                      >

                        <span className="panel-kicker">
                          DECREASES PREDICTION
                        </span>

                      </div>

                      {decreasingFeatures.map(
                        (item) => (

                          <div

                            className="importance-row"
                            key={
                              item.feature
                            }
                          >

                            <span>
                              {businessFeatureNames[item.feature]
                                ? `${businessFeatureNames[item.feature]} (${item.feature})`
                                : item.feature}
                            </span>

                            <div className="importance-track">

                              <div
                                className="importance-fill"
                                style={{
                                  width: `${
                                    (Math.abs(
                                      item.shap_value
                                    ) /
                                      maxShapValue) *
                                    100
                                  }%`,
                                }}
                              ></div>
                            </div>
                            <span>
                              {item.shap_value.toFixed(
                                3
                              )}
                            </span>
                          </div>

                        )
                      )}

                    </div>

                  ) : (

                    <div className="empty-state">

                      <div className="empty-icon">
                        ✦
                      </div>

                      <h4>
                        Explanation will appear here
                      </h4>

                      <p>
                        Select a customer record to
                        view the factors influencing
                        the prediction.
                      </p>
                    </div>
                  )}
                </>
              )}

          </div>

          {/* Global Explanation */}
          <div className="panel global-panel">
            <div className="panel-header">
              <div>
                <span className="panel-kicker">
                  GLOBAL EXPLANATION
                </span>
                <h3>
                  Feature Importance
                </h3>
              </div>

              <span className="panel-note">
                SHAP
              </span>

            </div>

            {globalLoading ? (

              <div className="empty-state">


                <div className="empty-icon">
                  ✦
                </div>

                <h4>
                  Loading feature importance...
                </h4>

                <p>
                  Calculating global SHAP importance.
                </p>

              </div>

            ) : globalError ? (

              <div className="empty-state">

                <div className="empty-icon">
                  !
                </div>

                <h4>
                  Feature importance unavailable
                </h4>

                <p>
                  {globalError}
                </p>

              </div>

            ) : globalExplanation ? (

              <>

                {/* Global Feature Importance */}
                <div className="importance-list">

                  {globalFeatures.map(
                    (item) => (

                      <div
                        className="importance-row"
                        key={
                          item.feature
                        }
                      >

                        <span>
                          {businessFeatureNames[item.feature]
                            ? `${businessFeatureNames[item.feature]} (${item.feature})`
                            : item.feature}
                        </span>

                        <div className="importance-track">

                          <div
                            className="importance-fill"
                            style={{
                              width: `${
                                (item.mean_absolute_shap /
                                  maxGlobalShapValue) *

                                100
                              }%`,
                            }}
                          ></div>

                        </div>

                        <span>
                          {item.mean_absolute_shap.toFixed(
                            3
                          )}
                        </span>

                      </div>

                    )
                  )}

                </div>

                {/* Business Insight */}
                <div className="insight-card">
                  <div className="insight-icon">
                    💡
                  </div>
                  <div>
                    <h3>
                      Business Insight
                    </h3>
                    {prediction &&
                    localExplanation &&
                    globalExplanation ? (
                      <>
                        <p>
                          The model predicts{' '}
                          <strong>
                            {
                              prediction.prediction_label
                            }
                          </strong>{' '}
                          for this customer with a{' '}
                          <strong>
                            {probability.toFixed(
                              2
                            )}%
                          </strong>{' '}
                          predicted default probability.
                          {topIncreasingFeatures.length >
                            0 && (
                            <>
                              {' '}
                              Factors increasing the
                              predicted default probability
                              include{' '}
                              <strong>
                                {topIncreasingFeatures.join(
                                  ', '
                                )}
                              </strong>
                            </>
                          )}
                          {topDecreasingFeatures.length >
                            0 && (
                            <>
                              {topIncreasingFeatures.length >
                              0
                                ? ', while '
                                : ' Factors that reduce the predicted probability include '}
                              <strong>
                                {topDecreasingFeatures.join(
                                  ', '
                                )}
                              </strong>
                              {topIncreasingFeatures.length >
                                0 &&
                                ' reduce the predicted probability'}
                            </>
                          )}
                          .
                          {topGlobalFeature && (
                            <>
                              {' '}
                              Across the dataset,{' '}
                              <strong>
                                {topGlobalFeature}
                              </strong>{' '}
                              has the highest mean absolute
                              SHAP value.
                            </>
                          )}
                        </p>

                        <p className="simple-business-explanation">
                          <strong>In simple terms:</strong>{' '}
                          The model considers this customer's
                          information and estimates the likelihood
                          of default based mainly on their recent
                          repayment behavior and other
                          credit-related information. Some factors
                          reduce the estimated risk, while others
                          increase it. The overall combination
                          results in a{' '}
                          <strong>
                            {prediction.prediction_label.toLowerCase()}
                          </strong>{' '}
                          prediction.
                        </p>
                      </>
                    ) : (
                      <p>
                        Business insights will appear after
                        the model prediction and SHAP
                        explanations are loaded.
                      </p>
                    )}
                  </div>
                </div>

              </>

            ) : null}

          </div>

        </section>

      </main>

    </div>
  )
}

export default App