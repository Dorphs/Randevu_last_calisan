import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import {
  Box,
  Container,
  Paper,
  Typography,
  Tab,
  Tabs,
  Grid,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { tr } from 'date-fns/locale'
import { startOfMonth, endOfMonth, subMonths, format } from 'date-fns'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

function Raporlar() {
  const { token } = useAuth()
  const [tabValue, setTabValue] = useState(0)
  const [ziyaretciVerileri, setZiyaretciVerileri] = useState(null)
  const [toplantiVerileri, setToplantiVerileri] = useState(null)
  const [baslangicTarihi, setBaslangicTarihi] = useState(new Date(new Date().setDate(1)))
  const [bitisTarihi, setBitisTarihi] = useState(new Date())
  const [filterType, setFilterType] = useState('date')
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)
  const [mevcutTarihler, setMevcutTarihler] = useState([])

  const fetchMevcutTarihler = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/raporlar/mevcut-tarihler/', {
        headers: {
          'Authorization': `Token ${token}`
        }
      })
      setMevcutTarihler(response.data.tarihler)

      // İlk mevcut tarihi seç
      if (response.data.tarihler.length > 0) {
        const ilkTarih = response.data.tarihler[0]
        setSelectedYear(ilkTarih.yil)
        setSelectedMonth(ilkTarih.ay)
        if (filterType === 'month') {
          const date = new Date(ilkTarih.yil, ilkTarih.ay - 1)
          setBaslangicTarihi(startOfMonth(date))
          setBitisTarihi(endOfMonth(date))
        }
      }
    } catch (error) {
      console.error('Mevcut tarihler alınırken hata:', error)
    }
  }

  useEffect(() => {
    fetchMevcutTarihler()
  }, [token])

  const handleFilterTypeChange = (event, newValue) => {
    if (newValue !== null) {
      setFilterType(newValue)
      if (newValue === 'month' && mevcutTarihler.length > 0) {
        const date = new Date(selectedYear, selectedMonth - 1)
        setBaslangicTarihi(startOfMonth(date))
        setBitisTarihi(endOfMonth(date))
      }
    }
  }

  // Mevcut yılları al
  const mevcutYillar = [...new Set(mevcutTarihler.map(t => t.yil))].sort((a, b) => b - a)

  // Seçili yıl için mevcut ayları al
  const mevcutAylar = mevcutTarihler
    .filter(t => t.yil === selectedYear)
    .sort((a, b) => b.ay - a.ay)

  const handleYearChange = (event) => {
    const year = event.target.value
    setSelectedYear(year)
    
    // Seçilen yıl için mevcut ilk ayı seç
    const yilAylari = mevcutTarihler.filter(t => t.yil === year)
    if (yilAylari.length > 0) {
      setSelectedMonth(yilAylari[0].ay)
      const date = new Date(year, yilAylari[0].ay - 1)
      setBaslangicTarihi(startOfMonth(date))
      setBitisTarihi(endOfMonth(date))
    }
  }

  const handleMonthChange = (event) => {
    const month = event.target.value
    setSelectedMonth(month)
    const date = new Date(selectedYear, month - 1)
    setBaslangicTarihi(startOfMonth(date))
    setBitisTarihi(endOfMonth(date))
  }

  const fetchData = async () => {
    try {
      const config = {
        headers: {
          'Authorization': `Token ${token}`
        },
        params: {
          baslangic: baslangicTarihi.toISOString().split('T')[0],
          bitis: bitisTarihi.toISOString().split('T')[0]
        }
      }

      const [ziyaretciResponse, toplantiResponse] = await Promise.all([
        axios.get('http://localhost:8000/api/raporlar/ziyaretci/', config),
        axios.get('http://localhost:8000/api/raporlar/toplanti/', config)
      ])

      setZiyaretciVerileri(ziyaretciResponse.data)
      setToplantiVerileri(toplantiResponse.data)
    } catch (error) {
      console.error('Veri çekme hatası:', error)
      if (error.response) {
        console.error('Hata detayı:', error.response.data)
      }
    }
  }

  useEffect(() => {
    fetchData()
  }, [token, baslangicTarihi, bitisTarihi])

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue)
  }

  // Tarih değişiklik işleyicileri
  const handleBaslangicTarihiChange = (newValue) => {
    setBaslangicTarihi(newValue)
  }

  const handleBitisTarihiChange = (newValue) => {
    setBitisTarihi(newValue)
  }

  // Randevu durumu verilerini pie chart için formatlama
  const formatRandevuData = (data) => {
    if (!data?.randevu_durumu) return []
    return [
      { name: 'Randevulu', value: data.randevu_durumu.randevulu },
      { name: 'Randevusuz', value: data.randevu_durumu.randevusuz }
    ]
  }

  // Günlük ziyaretçi verilerini line chart için formatlama
  const formatGunlukZiyaretler = (data) => {
    if (!data?.gunluk_ziyaretler) return []
    return data.gunluk_ziyaretler.map(item => ({
      tarih: new Date(item.tarih).toLocaleDateString(),
      toplam: item.toplam,
      'Kurum İçi': item.kurum_ici,
      'Kurum Dışı': item.kurum_disi
    }))
  }

  // Saat dağılımı verilerini bar chart için formatlama
  const formatSaatDagilimi = (data) => {
    if (!data?.saat_dagilimi) return []
    return data.saat_dagilimi.map(item => ({
      saat: `${item.saat}:00`,
      ziyaretci: item.toplam
    }))
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 2 }}>
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12}>
              <ToggleButtonGroup
                value={filterType}
                exclusive
                onChange={handleFilterTypeChange}
                aria-label="tarih filtre tipi"
                sx={{ mb: 2 }}
                fullWidth
              >
                <ToggleButton value="date" aria-label="tarih aralığı">
                  Tarih Aralığı
                </ToggleButton>
                <ToggleButton value="month" aria-label="ay seçimi">
                  Ay Seçimi
                </ToggleButton>
              </ToggleButtonGroup>
            </Grid>

            {filterType === 'date' ? (
              <>
                <Grid item xs={12} md={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={tr}>
                    <DatePicker
                      label="Başlangıç Tarihi"
                      value={baslangicTarihi}
                      onChange={handleBaslangicTarihiChange}
                      slotProps={{ textField: { fullWidth: true } }}
                      format="dd/MM/yyyy"
                    />
                  </LocalizationProvider>
                </Grid>
                <Grid item xs={12} md={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={tr}>
                    <DatePicker
                      label="Bitiş Tarihi"
                      value={bitisTarihi}
                      onChange={handleBitisTarihiChange}
                      slotProps={{ textField: { fullWidth: true } }}
                      format="dd/MM/yyyy"
                      minDate={baslangicTarihi}
                    />
                  </LocalizationProvider>
                </Grid>
              </>
            ) : (
              <>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Yıl</InputLabel>
                    <Select
                      value={selectedYear}
                      label="Yıl"
                      onChange={handleYearChange}
                    >
                      {mevcutYillar.map(year => (
                        <MenuItem key={year} value={year}>{year}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Ay</InputLabel>
                    <Select
                      value={selectedMonth}
                      label="Ay"
                      onChange={handleMonthChange}
                    >
                      {mevcutAylar.map(tarih => (
                        <MenuItem key={tarih.ay} value={tarih.ay}>
                          {tarih.ay_adi}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}
          </Grid>
        </Box>

        <Tabs value={tabValue} onChange={handleTabChange} centered>
          <Tab label="Ziyaretçi Raporları" />
          <Tab label="Toplantı Raporları" />
        </Tabs>

        {tabValue === 0 && ziyaretciVerileri && (
          <Box sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              {/* Günlük Ziyaretçi Grafiği */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Günlük Ziyaretçi Sayıları
                </Typography>
                <LineChart
                  width={800}
                  height={300}
                  data={formatGunlukZiyaretler(ziyaretciVerileri)}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="tarih" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="toplam" stroke="#8884d8" name="Toplam" />
                  <Line type="monotone" dataKey="Kurum İçi" stroke="#82ca9d" />
                  <Line type="monotone" dataKey="Kurum Dışı" stroke="#ffc658" />
                </LineChart>
              </Grid>

              {/* Saat Dağılımı Grafiği */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Saat Bazlı Ziyaretçi Dağılımı
                </Typography>
                <BarChart
                  width={500}
                  height={300}
                  data={formatSaatDagilimi(ziyaretciVerileri)}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="saat" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="ziyaretci" fill="#8884d8" name="Ziyaretçi Sayısı" />
                </BarChart>
              </Grid>

              {/* Randevu Durumu Pasta Grafiği */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Randevu Durumu Dağılımı
                </Typography>
                <PieChart width={400} height={300}>
                  <Pie
                    data={formatRandevuData(ziyaretciVerileri)}
                    cx={200}
                    cy={150}
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {formatRandevuData(ziyaretciVerileri).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </Grid>

              {/* En Çok Ziyaret Edilenler Tablosu */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  En Çok Ziyaret Edilenler
                </Typography>
                <Box sx={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr>
                        <th style={tableHeaderStyle}>Ad Soyad</th>
                        <th style={tableHeaderStyle}>Toplam Ziyaret</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ziyaretciVerileri.en_cok_ziyaret_edilenler.map((kisi, index) => (
                        <tr key={index}>
                          <td style={tableCellStyle}>
                            {kisi.ziyaret_edilen__first_name} {kisi.ziyaret_edilen__last_name}
                          </td>
                          <td style={tableCellStyle}>{kisi.toplam_ziyaret}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}

        {tabValue === 1 && toplantiVerileri && (
          <Box sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              {/* Günlük Toplantı Grafiği */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Günlük Toplantı Sayıları
                </Typography>
                <LineChart
                  width={800}
                  height={300}
                  data={toplantiVerileri.gunluk_toplantilar.map(item => ({
                    tarih: new Date(item.tarih).toLocaleDateString(),
                    toplam: item.toplam,
                    'Kurum İçi': item.kurum_ici,
                    'Kurum Dışı': item.kurum_disi
                  }))}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="tarih" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="toplam" stroke="#8884d8" name="Toplam" />
                  <Line type="monotone" dataKey="Kurum İçi" stroke="#82ca9d" />
                  <Line type="monotone" dataKey="Kurum Dışı" stroke="#ffc658" />
                </LineChart>
              </Grid>

              {/* Oda Kullanım İstatistikleri */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Toplantı Odası Kullanım İstatistikleri
                </Typography>
                <BarChart
                  width={500}
                  height={300}
                  data={toplantiVerileri.oda_kullanimi.map(item => ({
                    oda: item.oda__ad,
                    toplanti: item.toplam_toplanti
                  }))}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="oda" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="toplanti" fill="#8884d8" name="Toplantı Sayısı" />
                </BarChart>
              </Grid>

              {/* Saat Dağılımı Grafiği */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Saat Bazlı Toplantı Dağılımı
                </Typography>
                <BarChart
                  width={500}
                  height={300}
                  data={toplantiVerileri.saat_dagilimi.map(item => ({
                    saat: `${item.saat}:00`,
                    toplanti: item.toplam
                  }))}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="saat" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="toplanti" fill="#82ca9d" name="Toplantı Sayısı" />
                </BarChart>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>
    </Container>
  )
}

const tableHeaderStyle = {
  padding: '12px',
  textAlign: 'left',
  backgroundColor: '#f5f5f5',
  borderBottom: '2px solid #ddd'
}

const tableCellStyle = {
  padding: '8px',
  borderBottom: '1px solid #ddd'
}

export default Raporlar
