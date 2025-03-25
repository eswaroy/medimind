import React from 'react';
import { MessageSquare, User2, Grid, Users, MessageCircle, Maximize2, LogOut } from 'lucide-react';

// Mock data
const doctorData = {
  name: "Sarah Smith",
  role: "Doctor",
  avatar: "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&q=80&w=150&h=150"
};

const patientData = {
  name: "Ramesh Kumar",
  image: "https://images.unsplash.com/photo-1564564321837-a57b7070ac4f?auto=format&fit=crop&q=80&w=300&h=300",
  about: "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.",
  email: "rameshkumar@gmail.com",
  phone: "+91 8548521524",
  address: "345, Sarju Appt., Mota Varacha, Gujarat, India"
};

const visitHistory = [
  { date: "17 March 2025", treatment: "Check Up", status: "Prescription" },
  { date: "17 Feb 2025", treatment: "X-Ray", status: "Report" },
  { date: "17 March 2025", treatment: "Blood Test", status: "Report" }
];

const generalReport = [
  { name: "Heart Beat", value: 93, color: "bg-purple-500" },
  { name: "Blood Pressure", value: 89, color: "bg-green-500" },
  { name: "Sugar", value: 60, color: "bg-blue-500" },
  { name: "Haemoglobin", value: 80, color: "bg-red-500", unit: "%" }
];

function App() {
  const handleIconClick = () => {
    window.location.href = 'http://localhost:8501/';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-pink-100 to-white">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-24 bg-white shadow-lg flex flex-col items-center py-8">
        <div className="space-y-4 mb-8">
          <img src={doctorData.avatar} alt={doctorData.name} className="w-16 h-16 rounded-full" />
          <div className="text-center">
            <p className="text-sm font-semibold">{doctorData.name}</p>
            <p className="text-xs text-gray-500">{doctorData.role}</p>
          </div>
        </div>
        
        <div className="flex flex-col space-y-8 items-center flex-grow">
          <button className="p-3 rounded-xl bg-gray-100 hover:bg-gray-200">
            <Grid size={24} />
          </button>
          <button className="p-3 rounded-xl hover:bg-gray-100">
            <Users size={24} />
          </button>
          <button onClick={handleIconClick} className="p-3 rounded-xl hover:bg-gray-100">
            <MessageCircle size={24} />
          </button>
          <button className="p-3 rounded-xl hover:bg-gray-100">
            <Maximize2 size={24} />
          </button>
        </div>

        <button className="mt-auto p-3 rounded-xl hover:bg-gray-100">
          <LogOut size={24} />
        </button>
      </div>

      {/* Main Content */}
      <div className="ml-24 p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-navy-900">Profile</h1>
          <div className="flex space-x-4">
            <button onClick={handleIconClick} className="p-2 bg-white rounded-full shadow-md hover:shadow-lg">
              <User2 size={24} />
            </button>
            <button onClick={handleIconClick} className="p-2 bg-white rounded-full shadow-md hover:shadow-lg">
              <MessageSquare size={24} />
            </button>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-8 shadow-lg">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Patient Information</h2>
            <button className="px-6 py-2 bg-purple-500 text-white rounded-full hover:bg-purple-600">
              Start Session
            </button>
          </div>

          <div className="flex gap-8 mb-8">
            <img src={patientData.image} alt="Patient" className="w-48 h-48 rounded-2xl object-cover" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-4">About Patient</h3>
              <p className="text-gray-600 mb-6">{patientData.about}</p>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="font-semibold">Email</p>
                  <p className="text-gray-600">{patientData.email}</p>
                </div>
                <div>
                  <p className="font-semibold">Phone Number</p>
                  <p className="text-gray-600">{patientData.phone}</p>
                </div>
                <div>
                  <p className="font-semibold">Address</p>
                  <p className="text-gray-600">{patientData.address}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Past Visit History</h3>
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="py-2 px-4 text-left">Date</th>
                    <th className="py-2 px-4 text-left">Treatment</th>
                    <th className="py-2 px-4 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {visitHistory.map((visit, index) => (
                    <tr key={index}>
                      <td className="py-2 px-4">{visit.date}</td>
                      <td className="py-2 px-4">{visit.treatment}</td>
                      <td className="py-2 px-4">
                        <span className={`px-3 py-1 rounded-full text-sm ${
                          visit.status === 'Prescription' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
                        }`}>
                          {visit.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">General Report</h3>
              <div className="space-y-4">
                {generalReport.map((item, index) => (
                  <div key={index}>
                    <div className="flex justify-between mb-1">
                      <span>{item.name}</span>
                      <span>{item.value}{item.unit || ''}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`${item.color} h-2 rounded-full`}
                        style={{ width: `${item.value}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;