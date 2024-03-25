import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
np.random.seed(1)

N = 100
x = np.random.rand(N)
y = np.random.rand(N)
colors = np.random.rand(N)
sz = np.random.rand(N) * 30


df = {"a": [1,2,3,4,5,6,7,8,9],
      "b": [9,8,7,6,5,4,3,2,1]
}
df = pd.DataFrame(df)

fig = px.scatter(df, x="a", y="b", color="b")
st.write(fig)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["a"],
    y=df["b"],
    mode="markers",
    marker=go.scatter.Marker(
        size=sz,
        color=df["b"],
        # opacity=0.6,
        colorscale="Viridis"
    )
))
st.write(fig)

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=df["a"], 
    y=df["b"]
    ))

st.write(fig1)
if st.button("Download png file"):
    fig1.write_image("scatter.png")

st.write(df)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df["a"],
    y=df["b"],
    marker_color=df["b"], # You can still use colors for the bars
    opacity=1
))

# Additional settings (like title, axes labels) can be added here
st.write(fig)

if st.button("Download bar file"):
    fig.write_image("bar.png")