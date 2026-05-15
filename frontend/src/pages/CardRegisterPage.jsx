import { Link } from 'react-router-dom';
import { useState } from 'react';

import '../assets/styles/CardRegister.css';
import mesh from '../assets/images/mesh.png'
import logo from '../assets/images/logo-club360.png'
import eyeopen from '../assets/images/eye-open.png'
import eyeclosed from '../assets/images/eye-closed.png'
import redwarning from '../assets/images/warning-red.png'

import { toast } from 'react-toastify';

export default function CardRegisterPage(){

	// initial value for the array that represents the form values.
    const [formValue, setFormValue] = useState({ number: "", expirationDate: "", owner: "", cvv: ""});

    // error array for frontend form validations
    const [errors, setErrors] = useState({ number: "", expirationDate: "", owner: "", cvv: ""});

	const validateCardNumber = (number) => {
		const regex = /^\d{16}$/;
		return regex.test(number) ? "" : "Debe tener 16 dígitos";
	};

	const validateExpiration = (date) => {
		const regex = /^\d{4}-\d{2}$/; // YYYY-MM
		return regex.test(date) ? "" : "Formato YYYY-MM";
	};

	const validateCVV = (cvv) => {
		const regex = /^\d{3}$/;
		return regex.test(cvv) ? "" : "Debe tener 3 dígitos";
	};

	const validators = {
		number: validateCardNumber,
		expirationDate: validateExpiration,
		cvv: validateCVV,
	};


	// handle change updates form as it's inputted
	const handleChange = (e) => {
        const { name, value } = e.target;

		setFormValue({
			...formValue,
			[name]: value
		});

		setErrors({
			...errors,
			[name]: validators[name] ? validators[name](value) : ""
		});

    };

	

	// BACKEND INTERACTION should go here
	const handleSubmit = (e) => {
		e.preventDefault();

		const newErrors = {
			number: validateCardNumber(formValue.number),
			expirationDate: validateExpiration(formValue.expirationDate),
			cvv: validateCVV(formValue.cvv),
		};

		setErrors(newErrors);

		const hasErrors = Object.values(newErrors).some(err => err !== "");

		if (hasErrors) return; // prevents submitting if frontend validations fail

		toast.success("Tarjeta registrada correctamente"); // remplace with backend interaction
	};


	return(
			<div className="cardRegisterFormContainer">
				<form className="cardRegisterForm" onSubmit={handleSubmit}> 
					
					<h1 className="cardRegisterFormTitle">Registrar Tarjeta</h1>

					{/*NUMBER*/}
					<div className="formInput">
						<div className="labelRow">
							<label>Número de Tarjeta</label>

							<span className={`fieldError ${errors.number ? "show" : ""}`}>
								{errors.number}
							</span>
						</div>

						<div className="inputWrapper">
							<input
								className="cardRegisterInput"
								value={formValue.number}
								name="number"
								type="text"
								inputMode="numeric"
								pattern="[0-9]*"
								placeholder="1234 5678 9123 4567"
								onChange={handleChange}
								required
							/>
						</div>
					</div>

					{/*EXPIRATION DATE*/}
					<div className="formInput">

						<div className="labelRow">
							<label>Fecha de Vencimiento</label>

							<span className={`fieldError ${errors.expirationDate ? "show" : ""}`}>
								{errors.expirationDate}
							</span>
						</div>

						<div className="inputWrapper">
							<input
								className="cardRegisterInput"
								value={formValue.expirationDate}
								name="expirationDate"
								type="month"
								placeholder="YYYY-MM"
								onChange={handleChange}
								required
							/>
						</div>
					</div>

					{/*OWNER*/}
					<div className="formInput">

						<label>Titular</label>
						
						<div className="inputWrapper">
							<input
								className="cardRegisterInput"
								value={formValue.owner}
								name="owner"
								type="text"
								placeholder="Juan Perez"
								onChange={handleChange}
								required
							/>
						</div>
					</div>

					{/*CVV*/}
					<div className="formInput">

						<div className="labelRow">
							<label>CVV</label>

							<span className={`fieldError ${errors.cvv ? "show" : ""}`}>
								{errors.cvv}
							</span>
						</div>

						<div className="inputWrapper">
							<input
								className="cardRegisterInput"
								value={formValue.cvv}
								name="cvv"
								type="text"
								inputMode="numeric"
								pattern="[0-9]*"
								placeholder="123"
								onChange={handleChange}
								required
							/>
						</div>
					</div>

					<input type="submit" className="cardRegisterSUbmit" value="Registrar Tarjeta"/>

				</form>
			</div>
	)
}