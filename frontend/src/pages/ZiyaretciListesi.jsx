import React, { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Chip,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import { ziyaretciService, userService } from '../services/api'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

function ZiyaretciListesi() {
  const [ziyaretciler, setZiyaretciler] = useState([])
  const [kullanicilar, setKullanicilar] = useState([])
  const [open, setOpen] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [tamamlaDialogOpen, setTamamlaDialogOpen] = useState(false)
  const [selectedZiyaretci, setSelectedZiyaretci] = useState(null)
  const [formData, setFormData] = useState({
    ziyaret_nedeni: '',
    randevulu: false,
    randevu_zamani: null,
    ziyaret_zamani: dayjs().format('YYYY-MM-DDTHH:mm'),
    ziyaret_bitis_zamani: null,
    ziyaret_edilen_id: '',
    durum: 'BEKLIYOR',
    tur: 'KURUM_DISI',
    kurum_ici_ziyaretci_ids: [],
    kurum_disi_ziyaretciler_data: [],
    notlar: ''
  })
  const [tamamlaData, setTamamlaData] = useState(null)
  const [error, setError] = useState(null)

  const [kurumDisiZiyaretci, setKurumDisiZiyaretci] = useState({
    ad: '',
    soyad: '',
    telefon: '',
    kurum_unvan: ''
  })

  const DURUM_SECENEKLERI = [
    { value: 'BEKLIYOR', label: 'Bekliyor' },
    { value: 'GORUSME_BASLADI', label: 'Görüşme Başladı' },
    { value: 'TAMAMLANDI', label: 'Tamamlandı' },
    { value: 'IPTAL', label: 'İptal' },
  ]
  const TUR_SECENEKLERI = [
    { value: 'KURUM_ICI', label: 'Kurum İçi' },
    { value: 'KURUM_DISI', label: 'Kurum Dışı' },
  ]

  const fetchData = async () => {
    try {
      setError(null)
      const [ziyaretcilerRes, kullanicilarRes] = await Promise.all([
        ziyaretciService.getAll(),
        userService.getAll(),
      ])
      console.log('Ziyaretçiler yüklendi:', ziyaretcilerRes.data)
      console.log('Kullanıcılar yüklendi:', kullanicilarRes.data)
      setZiyaretciler(ziyaretcilerRes.data)
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

  // Form açıldığında kullanıcıları tekrar yükle
  useEffect(() => {
    if (open) {
      userService.getAll().then(
        (response) => {
          console.log('Form açıldığında kullanıcılar yüklendi:', response.data)
          setKullanicilar(response.data)
        },
        (error) => {
          console.error('Kullanıcı yükleme hatası:', error)
          setError('Kullanıcılar yüklenirken bir hata oluştu: ' + error.message)
        }
      )
    }
  }, [open])

  const handleOpenDialog = (ziyaretci = null) => {
    if (ziyaretci) {
      setFormData({
        ...ziyaretci,
        ziyaret_edilen_id: ziyaretci.ziyaret_edilen.id,
        kurum_ici_ziyaretci_ids: ziyaretci.kurum_ici_ziyaretciler?.map(k => k.id) || [],
        kurum_disi_ziyaretciler_data: ziyaretci.kurum_disi_ziyaretciler || []
      })
      setSelectedZiyaretci(ziyaretci)
    } else {
      setFormData({
        ziyaret_nedeni: '',
        randevulu: false,
        randevu_zamani: null,
        ziyaret_zamani: dayjs().format('YYYY-MM-DDTHH:mm'),
        ziyaret_edilen_id: '',
        durum: 'BEKLIYOR',
        tur: 'KURUM_DISI',
        kurum_ici_ziyaretci_ids: [],
        kurum_disi_ziyaretciler_data: [],
        notlar: ''
      })
      setSelectedZiyaretci(null)
    }
    setOpen(true)
  }

  const handleCloseDialog = () => {
    setFormData({
      ziyaret_nedeni: '',
      randevulu: false,
      randevu_zamani: null,
      ziyaret_zamani: dayjs().format('YYYY-MM-DDTHH:mm'),
      ziyaret_bitis_zamani: null,
      ziyaret_edilen_id: '',
      durum: 'BEKLIYOR',
      tur: 'KURUM_DISI',
      kurum_ici_ziyaretci_ids: [],
      kurum_disi_ziyaretciler_data: [],
      notlar: ''
    })
    setSelectedZiyaretci(null)
    setOpen(false)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    try {
      // Form validasyonu
      if (!formData.ziyaret_edilen_id) {
        setError('Ziyaret edilen kişiyi seçmelisiniz')
        return
      }

      if (!formData.ziyaret_nedeni) {
        setError('Ziyaret nedenini yazmalısınız')
        return
      }

      if (formData.tur === 'KURUM_ICI') {
        if (formData.kurum_ici_ziyaretci_ids.length === 0) {
          setError('En az bir kurum içi ziyaretçi seçmelisiniz')
          return
        }
      } else {
        if (formData.kurum_disi_ziyaretciler_data.length === 0) {
          setError('En az bir kurum dışı ziyaretçi eklemelisiniz')
          return
        }
      }

      const postData = {
        ...formData,
        // Randevulu değilse randevu_zamani null olmalı
        randevu_zamani: formData.randevulu ? formData.randevu_zamani : null,
      }

      if (selectedZiyaretci) {
        await ziyaretciService.update(selectedZiyaretci.id, postData)
      } else {
        await ziyaretciService.create(postData)
      }
      handleCloseDialog()
      fetchData()
    } catch (error) {
      console.error('Kaydetme hatası:', error)
      // Hata detaylarını göster
      if (error.response) {
        console.error('Hata detayları:', error.response.data)
        setError(error.response.data.detail || JSON.stringify(error.response.data))
      } else {
        setError('Bir hata oluştu: ' + error.message)
      }
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Bu ziyaretçi kaydını silmek istediğinize emin misiniz?')) {
      try {
        await ziyaretciService.delete(id)
        fetchData()
      } catch (error) {
        console.error('Silme hatası:', error)
      }
    }
  }

  const handleUpdate = async (ziyaretci) => {
    try {
      const updatedData = {
        ...ziyaretci,
        ziyaret_edilen_id: ziyaretci.ziyaret_edilen.id,
        kurum_ici_ziyaretci_ids: ziyaretci.kurum_ici_ziyaretciler?.map(k => k.id) || [],
        kurum_disi_ziyaretciler_data: ziyaretci.kurum_disi_ziyaretciler || []
      }
      await ziyaretciService.update(ziyaretci.id, updatedData)
      fetchData()
    } catch (error) {
      console.error('Güncelleme hatası:', error)
      setError('Güncelleme sırasında bir hata oluştu')
    }
  }

  const handleTamamla = (ziyaretci) => {
    setTamamlaData({
      ...ziyaretci,
      durum: 'TAMAMLANDI',
      ziyaret_bitis_zamani: dayjs().format('YYYY-MM-DDTHH:mm')
    })
    setSelectedZiyaretci(ziyaretci)
    setTamamlaDialogOpen(true)
  }

  const handleTamamlaSubmit = async () => {
    try {
      const updatedData = {
        ziyaret_nedeni: selectedZiyaretci.ziyaret_nedeni,
        randevulu: selectedZiyaretci.randevulu,
        randevu_zamani: selectedZiyaretci.randevu_zamani,
        ziyaret_zamani: selectedZiyaretci.ziyaret_zamani,
        ziyaret_bitis_zamani: tamamlaData.ziyaret_bitis_zamani,
        durum: 'TAMAMLANDI',
        tur: selectedZiyaretci.tur,
        notlar: selectedZiyaretci.notlar,
        ziyaret_edilen_id: selectedZiyaretci.ziyaret_edilen.id,
        kurum_ici_ziyaretci_ids: selectedZiyaretci.kurum_ici_ziyaretciler?.map(k => k.id) || [],
        kurum_disi_ziyaretciler_data: selectedZiyaretci.kurum_disi_ziyaretciler?.map(k => ({
          id: k.id,
          ad: k.ad,
          soyad: k.soyad,
          telefon: k.telefon,
          kurum_unvan: k.kurum_unvan
        })) || []
      }
      await ziyaretciService.update(selectedZiyaretci.id, updatedData)
      setTamamlaDialogOpen(false)
      fetchData()
    } catch (error) {
      console.error('Güncelleme hatası:', error)
      setError('Güncelleme sırasında bir hata oluştu')
    }
  }

  const calculateDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return '';
    
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
          Ziyaretçiler
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Yeni Ziyaretçi
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Ziyaret Nedeni</TableCell>
              <TableCell>Ziyaret Edilen</TableCell>
              <TableCell>Ziyaretçiler</TableCell>
              <TableCell>Ziyaret Zamanı</TableCell>
              <TableCell>Durum</TableCell>
              <TableCell>Süre</TableCell>
              <TableCell>İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {ziyaretciler.map((ziyaretci) => (
              <TableRow key={ziyaretci.id}>
                <TableCell>{ziyaretci.ziyaret_nedeni}</TableCell>
                <TableCell>
                  {ziyaretci.ziyaret_edilen?.first_name} {ziyaretci.ziyaret_edilen?.last_name}
                </TableCell>
                <TableCell>
                  {ziyaretci.kurum_ici_ziyaretciler?.map(user => 
                    `${user.first_name} ${user.last_name}`
                  ).join(', ')}
                  {ziyaretci.kurum_ici_ziyaretciler?.length > 0 && ziyaretci.kurum_disi_ziyaretciler?.length > 0 && ', '}
                  {ziyaretci.kurum_disi_ziyaretciler?.map(k => 
                    `${k.ad} ${k.soyad}${k.kurum_unvan ? ` - ${k.kurum_unvan}` : ''}`
                  ).join(', ')}
                </TableCell>
                <TableCell>
                  {dayjs(ziyaretci.ziyaret_zamani).format('DD/MM/YYYY HH:mm')}
                </TableCell>
                <TableCell>
                  {ziyaretci.durum === 'BEKLIYOR' ? 'Bekliyor' : 
                   ziyaretci.durum === 'GORUSME_BASLADI' ? 'Görüşme Başladı' : 
                   ziyaretci.durum === 'TAMAMLANDI' ? 'Tamamlandı' : 'İptal'}
                </TableCell>
                <TableCell>
                  {ziyaretci.durum === 'TAMAMLANDI' && calculateDuration(ziyaretci.ziyaret_zamani, ziyaretci.ziyaret_bitis_zamani)}
                </TableCell>
                <TableCell>
                  <IconButton
                    color="primary"
                    onClick={() => handleOpenDialog(ziyaretci)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    color="error"
                    onClick={() => handleDelete(ziyaretci.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                  {ziyaretci.durum !== 'TAMAMLANDI' && (
                    <IconButton
                      color="success"
                      onClick={() => handleTamamla(ziyaretci)}
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

      <Dialog open={open} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedZiyaretci ? 'Ziyaretçi Düzenle' : 'Yeni Ziyaretçi'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            {error && (
              <Typography color="error" sx={{ mb: 2 }}>
                {error}
              </Typography>
            )}
            <FormControl fullWidth margin="normal">
              <InputLabel>Ziyaretçi Türü</InputLabel>
              <Select
                value={formData.tur}
                onChange={(e) => {
                  const newTur = e.target.value
                  setFormData({
                    ...formData,
                    tur: newTur,
                    // Kurum içi seçildiğinde kişisel bilgileri temizle
                    ...(newTur === 'KURUM_ICI' && {
                      kurum_ici_ziyaretci_ids: []
                    }),
                    // Kurum dışı seçildiğinde kurum içi ziyaretçileri temizle
                    ...(newTur === 'KURUM_DISI' && {
                      kurum_disi_ziyaretciler_data: []
                    })
                  })
                }}
                label="Ziyaretçi Türü"
              >
                {TUR_SECENEKLERI.map((tur) => (
                  <MenuItem key={tur.value} value={tur.value}>
                    {tur.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {formData.tur === 'KURUM_ICI' ? (
              <FormControl fullWidth margin="normal" required>
                <InputLabel>Kurum İçi Ziyaretçiler</InputLabel>
                <Select
                  multiple
                  value={formData.kurum_ici_ziyaretci_ids || []}
                  onChange={(e) =>
                    setFormData({ ...formData, kurum_ici_ziyaretci_ids: e.target.value })
                  }
                  label="Kurum İçi Ziyaretçiler"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => {
                        const user = kullanicilar.find(k => k.id === value)
                        return (
                          <Chip
                            key={value}
                            label={`${user?.first_name} ${user?.last_name}`}
                          />
                        )
                      })}
                    </Box>
                  )}
                >
                  {kullanicilar.map((user) => (
                    <MenuItem key={user.id} value={user.id}>
                      {user.first_name} {user.last_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Kurum Dışı Ziyaretçiler
                  </Typography>
                  {formData.kurum_disi_ziyaretciler_data.map((ziyaretci, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Chip
                        label={`${ziyaretci.ad} ${ziyaretci.soyad}${ziyaretci.kurum_unvan ? ` - ${ziyaretci.kurum_unvan}` : ''}`}
                        onDelete={() => {
                          setFormData({
                            ...formData,
                            kurum_disi_ziyaretciler_data: formData.kurum_disi_ziyaretciler_data.filter((_, i) => i !== index)
                          })
                        }}
                      />
                    </Box>
                  ))}
                </Box>

                <Box sx={{ border: 1, borderColor: 'divider', p: 2, mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Yeni Ziyaretçi Ekle
                  </Typography>
                  <TextField
                    fullWidth
                    label="Ad"
                    value={kurumDisiZiyaretci.ad}
                    onChange={(e) =>
                      setKurumDisiZiyaretci({ ...kurumDisiZiyaretci, ad: e.target.value })
                    }
                    margin="normal"
                    required
                  />
                  <TextField
                    fullWidth
                    label="Soyad"
                    value={kurumDisiZiyaretci.soyad}
                    onChange={(e) =>
                      setKurumDisiZiyaretci({ ...kurumDisiZiyaretci, soyad: e.target.value })
                    }
                    margin="normal"
                    required
                  />
                  <TextField
                    fullWidth
                    label="Telefon"
                    value={kurumDisiZiyaretci.telefon}
                    onChange={(e) =>
                      setKurumDisiZiyaretci({ ...kurumDisiZiyaretci, telefon: e.target.value })
                    }
                    margin="normal"
                  />
                  <TextField
                    fullWidth
                    label="Kurum/Ünvan"
                    value={kurumDisiZiyaretci.kurum_unvan}
                    onChange={(e) =>
                      setKurumDisiZiyaretci({ ...kurumDisiZiyaretci, kurum_unvan: e.target.value })
                    }
                    margin="normal"
                  />
                  <Button
                    variant="contained"
                    onClick={() => {
                      if (!kurumDisiZiyaretci.ad || !kurumDisiZiyaretci.soyad) {
                        setError('Ad ve soyad zorunludur')
                        return
                      }
                      setFormData({
                        ...formData,
                        kurum_disi_ziyaretciler_data: [
                          ...formData.kurum_disi_ziyaretciler_data,
                          { ...kurumDisiZiyaretci }
                        ]
                      })
                      setKurumDisiZiyaretci({
                        ad: '',
                        soyad: '',
                        telefon: '',
                        kurum_unvan: ''
                      })
                    }}
                    sx={{ mt: 1 }}
                  >
                    Ziyaretçi Ekle
                  </Button>
                </Box>
              </>
            )}
            <FormControl fullWidth margin="normal" required>
              <InputLabel>Ziyaret Edilen</InputLabel>
              <Select
                value={formData.ziyaret_edilen_id || ''}
                onChange={(e) =>
                  setFormData({ ...formData, ziyaret_edilen_id: e.target.value })
                }
                label="Ziyaret Edilen"
              >
                {kullanicilar.map((kullanici) => (
                  <MenuItem key={kullanici.id} value={kullanici.id}>
                    {kullanici.first_name} {kullanici.last_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Ziyaret Nedeni"
              value={formData.ziyaret_nedeni}
              onChange={(e) =>
                setFormData({ ...formData, ziyaret_nedeni: e.target.value })
              }
              margin="normal"
              required
              multiline
              rows={4}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.randevulu}
                  onChange={(e) =>
                    setFormData({ ...formData, randevulu: e.target.checked })
                  }
                />
              }
              label="Randevulu"
            />

            {formData.randevulu && (
              <TextField
                fullWidth
                label="Randevu Zamanı"
                type="datetime-local"
                value={formData.randevu_zamani || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    randevu_zamani: e.target.value
                  })
                }
                margin="normal"
                InputLabelProps={{
                  shrink: true,
                }}
              />
            )}

            <FormControl fullWidth margin="normal">
              <InputLabel>Durum</InputLabel>
              <Select
                value={formData.durum}
                onChange={(e) => {
                  const newDurum = e.target.value
                  setFormData({ 
                    ...formData, 
                    durum: newDurum,
                    // Eğer durum tamamlandı ise ve bitiş zamanı yoksa, ziyaret zamanından 1 saat sonrasını ayarla
                    ...(newDurum === 'TAMAMLANDI' && !formData.ziyaret_bitis_zamani && {
                      ziyaret_bitis_zamani: formData.ziyaret_zamani 
                        ? dayjs(formData.ziyaret_zamani).add(1, 'hour').format('YYYY-MM-DDTHH:mm')
                        : dayjs().add(1, 'hour').format('YYYY-MM-DDTHH:mm')
                    })
                  })
                }}
                label="Durum"
              >
                <MenuItem value="BEKLIYOR">Bekliyor</MenuItem>
                <MenuItem value="GORUSME_BASLADI">Görüşme Başladı</MenuItem>
                <MenuItem value="TAMAMLANDI">Tamamlandı</MenuItem>
                <MenuItem value="IPTAL">İptal</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Ziyaret Zamanı"
              type="datetime-local"
              value={formData.ziyaret_zamani || ''}
              onChange={(e) =>
                setFormData({ ...formData, ziyaret_zamani: e.target.value })
              }
              margin="normal"
              InputLabelProps={{
                shrink: true,
              }}
            />

            {formData.durum === 'TAMAMLANDI' && (
              <TextField
                fullWidth
                label="Ziyaret Bitiş Zamanı"
                type="datetime-local"
                value={formData.ziyaret_bitis_zamani || ''}
                onChange={(e) =>
                  setFormData({ ...formData, ziyaret_bitis_zamani: e.target.value })
                }
                margin="normal"
                InputLabelProps={{
                  shrink: true,
                }}
              />
            )}

            <TextField
              fullWidth
              label="Notlar"
              value={formData.notlar}
              onChange={(e) =>
                setFormData({ ...formData, notlar: e.target.value })
              }
              margin="normal"
              multiline
              rows={4}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>İptal</Button>
            <Button onClick={handleSubmit} variant="contained">
              Kaydet
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Tamamla Dialog */}
      <Dialog open={tamamlaDialogOpen} onClose={() => setTamamlaDialogOpen(false)}>
        <DialogTitle>Ziyareti Tamamla</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="normal"
            label="Bitiş Zamanı"
            type="datetime-local"
            value={tamamlaData?.ziyaret_bitis_zamani || ''}
            onChange={(e) =>
              setTamamlaData({ ...tamamlaData, ziyaret_bitis_zamani: e.target.value })
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
}

export default ZiyaretciListesi
