using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System;

/* Example Code:
 * void Start() {
 *     udp = new SIMVRUDP();
 *     udp.OpenUDP();
 * }
 * void Update() {
 *     udp.SendData(0.0f,acc_vector,gyro_vector,tilt_vector);
 * }
 */

public class SIMVRUDP
{
    IPAddress m_localAddress;
    int m_localBindPort;
    IPEndPoint m_localEP, m_sendEP;

    UdpClient m_udpSock = null;

    // Constructor
    public SIMVRUDP(string sendip="127.0.0.1", int port=44444) {
        m_localAddress = IPAddress.Parse(sendip);
        m_localBindPort = port;

        m_localEP = new IPEndPoint(m_localAddress, m_localBindPort+1);
        m_sendEP = new IPEndPoint(m_localAddress, m_localBindPort);
    }

    ~SIMVRUDP() {
        CloseUDP();
    }

    public void OpenUDP()
    {
        if (IsOpened())  //not closed
            return;

        try{
            m_udpSock = new UdpClient(m_localEP);
        } catch (System.Exception e) {
            Debug.Log(e.ToString());
            m_udpSock = null;
        }
    }

    public void CloseUDP()
    {
        if (!IsOpened())
            return;

        m_udpSock.Close();
        m_udpSock=null;
    }

    public bool IsOpened(){
        return m_udpSock != null;
    }

    //timestamp = 経過時間(sec)
    //acc = オブジェクト重力無し加速度(m/sec^2)
    //gyro = オブジェクト角速度(deg/sec)
    //tilt = オブジェクト角度(deg)
    public bool SendData(float timestamp, Vector3 acc, Vector3 gyro, Vector3 tilt)
    {
        if (!IsOpened())
            return false;

        float[] senddata = { timestamp, acc.x, acc.y, acc.z, gyro.x, gyro.y, gyro.z, tilt.x, tilt.y, tilt.z };
        byte[] senddata_byte = new byte[senddata.Length*sizeof(float)];
        int retSize = 0;

        foreach(var value in senddata) {
            byte[] bitconv = System.BitConverter.GetBytes(value);   //little endian
            Array.Copy(bitconv, 0, senddata_byte, retSize, bitconv.Length);
            retSize += sizeof(float);
        }

        m_udpSock.Send(senddata_byte, senddata_byte.Length, m_sendEP);
        return false;
    }
}
