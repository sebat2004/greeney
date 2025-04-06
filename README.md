<img width="1507" alt="Home" src="https://github.com/user-attachments/assets/41392648-51eb-4ac0-8e62-3ff28fa8b7ad" />

# Greeney: Own Your Emissions

Greeney is a carbon footprint tracker that helps you measure, understand, and reduce your transportation-related emissions. The app calculates your carbon footprint from various transportation activities and provides insights to make more eco-conscious choices.

The app is built with Next.js, TypeScript, Tailwind CSS on the frontend and Flask, Python for the backend API services.

## 🚀 Features 🚀

- Calculate carbon emissions from multiple transportation categories (Uber/Lyft rides, food deliveries, flights) in kg CO₂e
- Track your historical carbon footprint data and energy consumption (kWh)
- Visualize your carbon impact and distance traveled (miles) through charts and metrics
- Compare your emissions against environmental benchmarks
- Google Maps API integration for accurate distance calculation

##  🧮 Emissions Calculation Method  🧮
Carbon emissions (CO₂e) = Carbon Intensity (g CO₂/kWh) × Energy Consumed (kWh)

## ⚡️ Tech Stack ⚡️

- Next.js
- TypeScript
- Tailwind CSS
- ShadCN
- Flask
- Python
- Google APIs (Distance Matrix, Geocoding, Gmail,OAuth 2.0)

## 🏃 Run Locally 🏃

To run the project, follow these steps:

1. Clone the repository
```bash
git clone https://github.com/yourusername/greeney.git
```

2. For the frontend setup:

See instructions in the web-client folder README.md

3. For the backend setup:

See instructions in the backend folder README.md

4. Open http://localhost:3000 with your browser to see the frontend and http://localhost:5000 for the API.

## 🤝 Contributing 🤝 ##
Contributions are welcome! If you have any questions, bug findings, or feature requests, feel free to open an issue.

## 📚 Acknowledgements 📚 ##
Lannelongue, L., Grealey, J., Inouye, M. (2021). Green Algorithms: Quantifying the Carbon Footprint of Computation. Advanced Science, 2100707. https://doi.org/10.1002/advs.202100707

## 📄 License 📄 ##
This project is supported by the [MIT License](https://opensource.org/license/MIT).

## ⚠️ Disclaimer ⚠️ ## 
Greeney is a project for educational and environmental awareness purposes. The carbon emission calculations are estimates based on available data and should not be considered as exact measurements for regulatory or compliance purposes.
