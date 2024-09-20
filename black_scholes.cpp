#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>
#include <iostream>

namespace py = pybind11;

class BlackScholes {
public:
    BlackScholes() {}

    double blsprice(char cp_flag, double S, double X, double T, double r, double v) {
        double d1 = (std::log(S / X) + (r + 0.5 * v * v) * T) / (v * std::sqrt(T));
        double d2 = d1 - v * std::sqrt(T);
        if (cp_flag == 'c') {
            return S * norm_cdf(d1) - X * std::exp(-r * T) * norm_cdf(d2);
        } else {
            return X * std::exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1);
        }
    }

    double blsdelta(char cp_flag, double S, double X, double T, double r, double v) {
        double d1 = (std::log(S / X) + (r + 0.5 * v * v) * T) / (v * std::sqrt(T));
        if (cp_flag == 'c') {
            return norm_cdf(d1);
        } else {
            return norm_cdf(d1) - 1.0;
        }
    }

    double blsimpv(char cp_flag, double S, double X, double T, double r, double C, double sigma, double tol = 1e-6, int max_iterations = 100) {
        double low = 0.0;
        double high = 5.0;
        for (int i = 0; i < max_iterations; i++) {
            double mid = (low + high) / 2.0;
            double price = blsprice(cp_flag, S, X, T, r, mid);
            if (std::abs(price - C) < tol) {
                return mid;
            }
            if (price > C) {
                high = mid;
            } else {
                low = mid;
            }
        }
        return (low + high) / 2.0;
    }

private:
    double norm_cdf(double x) {
        return 0.5 * std::erfc(-x * std::sqrt(0.5));
    }
};

PYBIND11_MODULE(black_scholes, m) {
    py::class_<BlackScholes>(m, "BlackScholes")
        .def(py::init<>())
        .def("blsprice", &BlackScholes::blsprice)
        .def("blsdelta", &BlackScholes::blsdelta)
        .def("blsimpv", &BlackScholes::blsimpv);
}
