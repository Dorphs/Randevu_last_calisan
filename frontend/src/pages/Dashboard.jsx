import React from 'react'
import { Typography, Grid, Paper, Box } from '@mui/material'

function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Ana Sayfa
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Hoş Geldiniz
            </Typography>
            <Typography>
              Toplantı ve Ziyaretçi Takip Sistemine hoş geldiniz. Sol menüden işlem yapmak istediğiniz bölümü seçebilirsiniz.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
