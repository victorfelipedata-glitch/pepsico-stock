    )
    st.caption(f"Fórmula base basada en el histórico comercial de {cedis_seleccionado}.")

with col3:
    st.metric(
        label="Valor Esperado de Pérdida (MXN)",
        value=f"${valor_esperado_perdida:,.2f}",
        delta="Costo de oportunidad estimado" if probabilidad_quiebre > 0 else "Sin riesgo financiero",
        delta_color="inverse" if probabilidad_quiebre > 0 else "normal"
    )
    st.caption("Pérdida monetaria ponderada por la probabilidad de desabasto comercial.")

st.markdown("### 📈 Proyección de Inventarios (10,000 Líneas de Tiempo Virtuales)")

# Graficar resultados de Monte Carlo
fig, ax = plt.subplots(figsize=(10, 4.5))
dias = np.arange(horizonte_dias + 1)

# Graficar una muestra de trayectorias para no saturar la pantalla
muestra_trayectorias = min(100, simulaciones)
for s in range(muestra_trayectorias):
    alpha_value = 0.15 if probabilidad_quiebre > 40 else 0.1
    color_line = "#e63946" if matriz_inventarios[s, lead_time] == 0 else "#4a90e2"
    ax.plot(dias, matriz_inventarios[s, :], color=color_line, alpha=alpha_value, linewidth=1)

# Línea promedio
inventario_promedio = np.mean(matriz_inventarios, axis=0)
ax.plot(dias, inventario_promedio, color="#002F6C", linewidth=2.5, label="Inventario Promedio Esperado")

# Líneas guía de control
ax.axvline(x=lead_time, color="#f4a261", linestyle="--", linewidth=2, label=f"Llegada del Camión (Día {lead_time})")
ax.axhline(y=0, color="black", linestyle="-", linewidth=1.5)
ax.fill_between(dias, 0, -50, color="#e63946", alpha=0.05)

ax.set_title(f"Simulación de Trayectorias para {producto_seleccionado} en {cedis_seleccionado}", fontsize=11, fontweight='bold', color="#002F6C")
ax.set_xlabel("Línea de Tiempo (Días)", fontsize=9)
ax.set_ylabel("Cajas Disponibles en Stock", fontsize=9)
ax.set_xlim(0, horizonte_dias)
ax.set_ylim(bottom=-10)
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend(loc="upper right", fontsize=8)

st.pyplot(fig)

# Tabla de recomendaciones accionables para Operaciones
st.markdown("### 📋 Recomendación Automatizada para la Mesa de Control")
if probabilidad_quiebre > 40:
    st.error(f"⚠️ **ACCIÓN REQUERIDA INMEDIATA:** El modelo indica un riesgo crítico en {cedis_seleccionado}. Se sugiere adelantar el envío de reabastecimiento para reducir el Lead Time a menos de {max(1, lead_time-1)} días o emitir una orden de transferencia de stock inter-CEDIS de al menos {int(demanda_ajustada * lead_time - inventario_inicial)} cajas de {producto_seleccionado}.")
elif probabilidad_quiebre > 10:
    st.warning(f"⚡ **MONITOREO ACTIVADO:** El riesgo es moderado. Monitorear los pedidos del canal moderno durante las próximas 24 horas. No se requiere envío de emergencia pero sí priorizar la descarga en el andén cuando llegue el transporte.")
else:
    st.success("✅ **ESTADO ÓPTIMO:** Los niveles de inventario actuales cubren perfectamente la variabilidad de la demanda probabilística de Poisson hasta la llegada del próximo embarque.")
