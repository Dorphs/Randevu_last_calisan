import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material'
import { toplantiService, toplantiOdasiService, userService } from '../services/api'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

function ToplantiListesi() {
  const [toplantilar, setToplantilar] = useState([])
  const [odalar, setOdalar] = useState([])
  const [kullanicilar, setKullanicilar] = useState([])
  const [open, setOpen] = useState(false)
  const [tamamlaDialogOpen, setTamamlaDialogOpen] = useState(false)
  const [selectedToplanti, setSelectedToplanti] = useState(null)
  const [error, setError] = useState(null)

  const DURUM_SECENEKLERI = [
    { value: 'BEKLIYOR', label: 'Bekliyor' },
    { value: 'DEVAM_EDIYOR', label: 'Devam Ediyor' },
    { value: 'TAMAMLANDI', label: 'Tamamlandı' },
    { value: 'IPTAL', label: 'İptal' },
  ]

  const TUR_SECENEKLERI = [
    { value: 'KURUM_ICI', label: 'Kurum İçi' },
    { value: 'ONLINE', label: 'Online' },
    { value: 'HIBRIT', label: 'Hibrit' },
  ]

  const initialFormData = {
    baslik: '',
    konu: '',
    baslangic_zamani: null,
    bitis_zamani: null,
    oda_id: '',
    olusturan_id: '',
    durum: 'BEKLIYOR',
    tur: 'KURUM_ICI',
    katilimci_ids: [],
    kurum_disi_katilimcilar_data: [],
    notlar: ''
  }

  const [formData, setFormData] = useState(initialFormData)
  const [tamamlaData, setTamamlaData] = useState(null)

  const [kurumDisiKatilimci, setKurumDisiKatilimci] = useState({
    ad: '',
    soyad: '',
    kurum_unvan: ''
  })

  const fetchData = async () => {
    try {
      setError(null)
      const [toplantilarRes, odalarRes, kullanicilarRes] = await Promise.all([
        toplantiService.getAll(),
        toplantiOdasiService.getAll(),
        userService.getAll(),
      ])
      console.log('Toplantılar yüklendi:', toplantilarRes.data)
      console.log('Odalar yüklendi:', odalarRes.data)
      console.log('Kullanıcılar yüklendi:', kullanicilarRes.data)
      setToplantilar(toplantilarRes.data)
      setOdalar(odalarRes.data)
      setKullanicilar(kullanicilarRes.data)
    } catch (error) {
      console.error('Veri yükleme hatası:', error)
      setError('Veriler yüklenirken bir hata oluştu: ' + error.message)
    }
  }

  // Component mount olduğunda verileri yükle
  useEffect(() => {
    fetchData()
  }, [])

  // Form açıldığında kullanıcıları ve odaları tekrar yükle
  useEffect(() => {
    if (open) {
      Promise.all([
        userService.getAll(),
        toplantiOdasiService.getAll()
      ]).then(
        ([kullanicilarRes, odalarRes]) => {
          console.log('Form açıldığında kullanıcılar yüklendi:', kullanicilarRes.data)
          console.log('Form açıldığında odalar yüklendi:', odalarRes.data)
          setKullanicilar(kullanicilarRes.data)
          setOdalar(odalarRes.data)
        },
        (error) => {
          console.error('Veri yükleme hatası:', error)
          setError('Veriler yüklenirken bir hata oluştu: ' + error.message)
        }
      )
    }
  }, [open])

  const handleOpenDialog = (toplanti = null) => {
    if (toplanti) {
      setFormData({
        baslik: toplanti.baslik,
        konu: toplanti.konu,
        baslangic_zamani: format(new Date(toplanti.baslangic_zamani), "yyyy-MM-dd'T'HH:mm"),
        bitis_zamani: format(new Date(toplanti.bitis_zamani), "yyyy-MM-dd'T'HH:mm"),
        oda_id: toplanti.oda.id,
        olusturan_id: toplanti.olusturan.id,
        durum: toplanti.durum,
        tur: toplanti.tur,
        katilimci_ids: toplanti.katilimcilar.map(k => k.id),
        kurum_disi_katilimcilar_data: toplanti.kurum_disi_katilimcilar,
        notlar: toplanti.notlar || ''
      })
      setSelectedToplanti(toplanti)
    } else {
      setFormData({
        baslik: '',
        konu: '',
        baslangic_zamani: dayjs().format('YYYY-MM-DDTHH:mm'),
        bitis_zamani: dayjs().add(1, 'hour').format('YYYY-MM-DDTHH:mm'),
        oda_id: '',
        olusturan_id: 1, // user.id
        durum: 'BEKLIYOR',
        tur: 'KURUM_ICI',
        katilimci_ids: [],
        kurum_disi_katilimcilar_data: [],
        notlar: ''
      })
      setSelectedToplanti(null)
    }
    setOpen(true)
  }

  const handleCloseDialog = () => {
    setOpen(false)
    setSelectedToplanti(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      // Debug için form verilerini konsola yazdır
      console.log('Form verileri:', formData)

      // Zorunlu alanları kontrol et
      const requiredFields = ['baslik', 'baslangic_zamani', 'oda_id']
      const missingFields = requiredFields.filter(field => !formData[field])
      
      if (missingFields.length > 0) {
        setError(`Lütfen zorunlu alanları doldurun: ${missingFields.join(', ')}`)
        return
      }

      // Başlangıç zamanı bitiş zamanından önce olmalı
      if (formData.baslangic_zamani && formData.bitis_zamani && new Date(formData.baslangic_zamani) >= new Date(formData.bitis_zamani)) {
        setError('Başlangıç zamanı bitiş zamanından önce olmalıdır')
        return
      }

      const postData = {
        ...formData,
        // oda_id ve katilimci_ids'leri number olarak gönder
        oda_id: Number(formData.oda_id),
        katilimci_ids: formData.katilimci_ids.map(id => Number(id))
      }

      // Debug için gönderilecek verileri konsola yazdır
      console.log('Gönderilecek veriler:', postData)

      if (selectedToplanti) {
        await toplantiService.update(selectedToplanti.id, postData)
      } else {
        await toplantiService.create(postData)
      }
      handleCloseDialog()
      fetchData()
    } catch (error) {
      console.error('Kaydetme hatası:', error)
      if (error.response) {
        console.error('Hata detayları:', error.response.data)
        setError(error.response.data.detail || JSON.stringify(error.response.data))
      } else {
        setError('Bir hata oluştu: ' + error.message)
      }
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Bu toplantıyı silmek istediğinize emin misiniz?')) {
      try {
        await toplantiService.delete(id)
        fetchData()
      } catch (error) {
        console.error('Silme hatası:', error)
      }
    }
  }

  const handleUpdate = async (toplanti) => {
    try {
      const updatedData = {
        ...toplanti,
        oda_id: toplanti.oda.id,
        olusturan_id: toplanti.olusturan.id,
        katilimci_ids: toplanti.katilimcilar?.map(k => k.id) || [],
        kurum_disi_katilimcilar_data: toplanti.kurum_disi_katilimcilar || []
      }
      await toplantiService.update(toplanti.id, updatedData)
      fetchData()
    } catch (error) {
      console.error('Güncelleme hatası:', error)
      setError('Güncelleme sırasında bir hata oluştu')
    }
  }

  const handleTamamla = (toplanti) => {
    // Tamamla butonuna basıldığında dialog'u aç
    setTamamlaData({
      ...toplanti,
      durum: 'TAMAMLANDI',
      bitis_zamani: dayjs().format('YYYY-MM-DDTHH:mm')
    })
    setSelectedToplanti(toplanti)
    setTamamlaDialogOpen(true)
  }

  const handleTamamlaSubmit = async () => {
    try {
      const updatedData = {
        ...selectedToplanti,
        durum: 'TAMAMLANDI',
        bitis_zamani: tamamlaData.bitis_zamani,
        oda_id: selectedToplanti.oda.id,
        olusturan_id: selectedToplanti.olusturan.id,
        katilimci_ids: selectedToplanti.katilimcilar?.map(k => k.id) || [],
        kurum_disi_katilimcilar_data: selectedToplanti.kurum_disi_katilimcilar || []
      }
      await toplantiService.update(selectedToplanti.id, updatedData)
      setTamamlaDialogOpen(false)
      fetchData()
    } catch (error) {
      console.error('Güncelleme hatası:', error)
      setError('Güncelleme sırasında bir hata oluştu')
    }
  }

  const calculateDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return null;
    
    const start = dayjs(startTime);
    const end = dayjs(endTime);
    const diff = end.diff(start);
    const duration = dayjs.duration(diff);
    
    const hours = Math.floor(duration.asHours());
    const minutes = duration.minutes();
    
    if (hours > 0) {
      return `${hours} saat ${minutes} dakika`;
    }
    return `${minutes} dakika`;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Toplantılar
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Yeni Toplantı
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Başlık</TableCell>
              <TableCell>Başlangıç</TableCell>
              <TableCell>Oda</TableCell>
              <TableCell>Tür</TableCell>
              <TableCell>Durum</TableCell>
              <TableCell>Süre</TableCell>
              <TableCell>Katılımcılar</TableCell>
              <TableCell>İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {toplantilar.map((toplanti) => (
              <TableRow key={toplanti.id}>
                <TableCell>{toplanti.baslik}</TableCell>
                <TableCell>
                  {dayjs(toplanti.baslangic_zamani).format('DD/MM/YYYY HH:mm')}
                </TableCell>
                <TableCell>{toplanti.oda.ad}</TableCell>
                <TableCell>
                  {toplanti.tur === 'KURUM_ICI' ? 'Kurum İçi' : 'Kurum Dışı'}
                </TableCell>
                <TableCell>
                  {toplanti.durum === 'BEKLIYOR' ? 'Bekliyor' : 
                   toplanti.durum === 'DEVAM_EDIYOR' ? 'Devam Ediyor' : 
                   toplanti.durum === 'TAMAMLANDI' ? 'Tamamlandı' : 'İptal'}
                </TableCell>
                <TableCell>
                  {toplanti.durum === 'TAMAMLANDI' && calculateDuration(toplanti.baslangic_zamani, toplanti.bitis_zamani)}
                </TableCell>
                <TableCell>
                  {toplanti.katilimcilar?.map(user => 
                    `${user.first_name} ${user.last_name}`
                  ).join(', ')}
                  {toplanti.katilimcilar?.length > 0 && toplanti.kurum_disi_katilimcilar?.length > 0 && ', '}
                  {toplanti.kurum_disi_katilimcilar?.map(k => 
                    `${k.ad} ${k.soyad}${k.kurum_unvan ? ` - ${k.kurum_unvan}` : ''}`
                  ).join(', ')}
                </TableCell>
                <TableCell>
                  <IconButton
                    color="primary"
                    onClick={() => handleOpenDialog(toplanti)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    color="error"
                    onClick={() => handleDelete(toplanti.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                  {toplanti.durum !== 'TAMAMLANDI' && (
                    <IconButton
                      color="success"
                      onClick={() => handleTamamla(toplanti)}
                    >
                      <CheckCircleIcon />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedToplanti ? 'Toplantı Düzenle' : 'Yeni Toplantı'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          <Box component="form" sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Başlık"
              name="baslik"
              value={formData.baslik}
              onChange={(e) =>
                setFormData({ ...formData, baslik: e.target.value })
              }
              margin="normal"
            />
            <TextField
              fullWidth
              label="Konu"
              name="konu"
              value={formData.konu}
              onChange={(e) => setFormData({ ...formData, konu: e.target.value })}
              margin="normal"
              multiline
              rows={3}
            />
            <TextField
              fullWidth
              label="Başlangıç Zamanı"
              name="baslangic_zamani"
              type="datetime-local"
              value={formData.baslangic_zamani}
              onChange={(e) =>
                setFormData({ ...formData, baslangic_zamani: e.target.value })
              }
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <FormControl fullWidth margin="normal" required>
              <InputLabel>Toplantı Odası</InputLabel>
              <Select
                value={formData.oda_id}
                onChange={(e) =>
                  setFormData({ ...formData, oda_id: e.target.value })
                }
                label="Toplantı Odası"
              >
                {odalar.map((oda) => (
                  <MenuItem key={oda.id} value={oda.id}>
                    {oda.ad} ({oda.kapasite} kişilik)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth margin="normal" required>
              <InputLabel>Oluşturan</InputLabel>
              <Select
                value={formData.olusturan_id}
                onChange={(e) =>
                  setFormData({ ...formData, olusturan_id: e.target.value })
                }
                label="Oluşturan"
              >
                {kullanicilar.map((kullanici) => (
                  <MenuItem key={kullanici.id} value={kullanici.id}>
                    {kullanici.first_name} {kullanici.last_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth margin="normal" required>
              <InputLabel>Katılımcılar</InputLabel>
              <Select
                multiple
                value={formData.katilimci_ids}
                onChange={(e) =>
                  setFormData({ ...formData, katilimci_ids: e.target.value })
                }
                label="Katılımcılar"
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => {
                      const user = kullanicilar.find(k => k.id === value)
                      return (
                        <Chip
                          key={value}
                          label={`${user?.first_name} ${user?.last_name}`}
                          onDelete={() => {
                            setFormData({
                              ...formData,
                              katilimci_ids: formData.katilimci_ids.filter(id => id !== value)
                            })
                          }}
                        />
                      )
                    })}
                  </Box>
                )}
              >
                {kullanicilar.map((kullanici) => (
                  <MenuItem key={kullanici.id} value={kullanici.id}>
                    {kullanici.first_name} {kullanici.last_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Kurum Dışı Katılımcılar
              </Typography>
              {formData.kurum_disi_katilimcilar_data.map((katilimci, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Chip
                    label={`${katilimci.ad} ${katilimci.soyad}${katilimci.kurum_unvan ? ` - ${katilimci.kurum_unvan}` : ''}`}
                    onDelete={() => {
                      setFormData({
                        ...formData,
                        kurum_disi_katilimcilar_data: formData.kurum_disi_katilimcilar_data.filter((_, i) => i !== index)
                      })
                    }}
                  />
                </Box>
              ))}
            </Box>

            <Box sx={{ border: 1, borderColor: 'divider', p: 2, mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Yeni Kurum Dışı Katılımcı Ekle
              </Typography>
              <TextField
                fullWidth
                label="Ad"
                value={kurumDisiKatilimci.ad}
                onChange={(e) =>
                  setKurumDisiKatilimci({ ...kurumDisiKatilimci, ad: e.target.value })
                }
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Soyad"
                value={kurumDisiKatilimci.soyad}
                onChange={(e) =>
                  setKurumDisiKatilimci({ ...kurumDisiKatilimci, soyad: e.target.value })
                }
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Kurum/Ünvan"
                value={kurumDisiKatilimci.kurum_unvan}
                onChange={(e) =>
                  setKurumDisiKatilimci({ ...kurumDisiKatilimci, kurum_unvan: e.target.value })
                }
                margin="normal"
              />
              <Button
                variant="contained"
                onClick={() => {
                  if (!kurumDisiKatilimci.ad || !kurumDisiKatilimci.soyad) {
                    setError('Ad ve soyad zorunludur')
                    return
                  }
                  setFormData({
                    ...formData,
                    kurum_disi_katilimcilar_data: [
                      ...formData.kurum_disi_katilimcilar_data,
                      { ...kurumDisiKatilimci }
                    ]
                  })
                  setKurumDisiKatilimci({
                    ad: '',
                    soyad: '',
                    kurum_unvan: ''
                  })
                }}
                sx={{ mt: 1 }}
              >
                Katılımcı Ekle
              </Button>
            </Box>

            <FormControl fullWidth margin="normal">
              <InputLabel>Durum</InputLabel>
              <Select
                value={formData.durum}
                onChange={(e) => {
                  const newDurum = e.target.value
                  setFormData({ 
                    ...formData, 
                    durum: newDurum,
                    // Eğer durum tamamlandı ise ve bitiş zamanı yoksa, başlangıç zamanından 1 saat sonrasını ayarla
                    ...(newDurum === 'TAMAMLANDI' && !formData.bitis_zamani && {
                      bitis_zamani: formData.baslangic_zamani 
                        ? dayjs(formData.baslangic_zamani).add(1, 'hour').format('YYYY-MM-DDTHH:mm')
                        : dayjs().add(1, 'hour').format('YYYY-MM-DDTHH:mm')
                    })
                  })
                }}
                label="Durum"
              >
                <MenuItem value="BEKLIYOR">Bekliyor</MenuItem>
                <MenuItem value="DEVAM_EDIYOR">Devam Ediyor</MenuItem>
                <MenuItem value="TAMAMLANDI">Tamamlandı</MenuItem>
                <MenuItem value="IPTAL">İptal</MenuItem>
              </Select>
            </FormControl>

            {/* Bitiş zamanını sadece durum tamamlandı olduğunda göster */}
            {formData.durum === 'TAMAMLANDI' && (
              <TextField
                fullWidth
                label="Bitiş Zamanı"
                type="datetime-local"
                value={formData.bitis_zamani || ''}
                onChange={(e) =>
                  setFormData({ ...formData, bitis_zamani: e.target.value })
                }
                margin="normal"
                InputLabelProps={{
                  shrink: true,
                }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>İptal</Button>
          <Button onClick={handleSubmit} variant="contained">
            Kaydet
          </Button>
        </DialogActions>
      </Dialog>

      {/* Tamamla Dialog */}
      <Dialog open={tamamlaDialogOpen} onClose={() => setTamamlaDialogOpen(false)}>
        <DialogTitle>Toplantıyı Tamamla</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="normal"
            label="Bitiş Zamanı"
            type="datetime-local"
            value={tamamlaData?.bitis_zamani || ''}
            onChange={(e) =>
              setTamamlaData({ ...tamamlaData, bitis_zamani: e.target.value })
            }
            InputLabelProps={{ shrink: true }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTamamlaDialogOpen(false)}>İptal</Button>
          <Button onClick={handleTamamlaSubmit} variant="contained" color="primary">
            Tamamla
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Toplantılar
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Yeni Toplantı
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Başlık</TableCell>
              <TableCell>Başlangıç</TableCell>
              <TableCell>Oda</TableCell>
              <TableCell>Tür</TableCell>
              <TableCell>Durum</TableCell>
              <TableCell>Süre</TableCell>
              <TableCell>Katılımcılar</TableCell>
              <TableCell>İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {toplantilar.map((toplanti) => (
              <TableRow key={toplanti.id}>
                <TableCell>{toplanti.baslik}</TableCell>
                <TableCell>
                  {dayjs(toplanti.baslangic_zamani).format('DD/MM/YYYY HH:mm')}
                </TableCell>
                <TableCell>{toplanti.oda.ad}</TableCell>
                <TableCell>
                  {toplanti.tur === 'KURUM_ICI' ? 'Kurum İçi' : 'Kurum Dışı'}
                </TableCell>
                <TableCell>
                  {toplanti.durum === 'BEKLIYOR' ? 'Bekliyor' : 
                   toplanti.durum === 'DEVAM_EDIYOR' ? 'Devam Ediyor' : 
                   toplanti.durum === 'TAMAMLANDI' ? 'Tamamlandı' : 'İptal'}
                </TableCell>
                <TableCell>
                  {toplanti.durum === 'TAMAMLANDI' && calculateDuration(toplanti.baslangic_zamani, toplanti.bitis_zamani)}
                </TableCell>
                <TableCell>
                  {toplanti.katilimcilar?.map(user => 
                    `${user.first_name} ${user.last_name}`
                  ).join(', ')}
                  {toplanti.katilimcilar?.length > 0 && toplanti.kurum_disi_katilimcilar?.length > 0 && ', '}
                  {toplanti.kurum_disi_katilimcilar?.map(k => 
                    `${k.ad} ${k.soyad}${k.kurum_unvan ? ` - ${k.kurum_unvan}` : ''}`
                  ).join(', ')}
                </TableCell>
                <TableCell>
                  <IconButton
                    color="primary"
                    onClick={() => handleOpenDialog(toplanti)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    color="error"
                    onClick={() => handleDelete(toplanti.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                  {toplanti.durum !== 'TAMAMLANDI' && (
                    <IconButton
                      color="success"
                      onClick={() => handleTamamla(toplanti)}
                    >
                      <CheckCircleIcon />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

export default ToplantiListesi
