import plotly.graph_objects as go

# Sample data
categories = [
    "Quality of Food", "Taste/Flavor", "Cleanliness", "Waitstaff", 
    "Food Cost", "Cash Discounts", "Online Reservation", 
    "Wifi Availability", "Online Ordering", "Drive-thru"
]
positive = [68, 98, 50, 74, 65, 59, 83, 79, 68, 71]
negative = [34, 24, 75, 29, 36, 44, 15, 29, 32, 30]

# Create the figure
fig = go.Figure()

# Add positive sentiment bars
fig.add_trace(go.Bar(
    x=categories,
    y=positive,
    name='Positive',
    marker_color='lightgreen'
))

# Add negative sentiment bars (inverted for proper stacking)
fig.add_trace(go.Bar(
    x=categories,
    y=[-n for n in negative],  # Negative values for downward stacking
    name='Negative',
    marker_color='salmon'
))

# Update layout for styling
fig.update_layout(
    title="Restaurant Customers Sentiment Analysis",
    barmode='relative',  # Enables stacking
    xaxis=dict(title='Categories'),
    yaxis=dict(
        title='Sentiment (%)',
        zeroline=True,  # Ensure a zero line is present
        zerolinewidth=2,
        zerolinecolor='black'
    ),
    legend=dict(title="Sentiment"),
    template='plotly_white'
)

# Show the plot
fig.show()
