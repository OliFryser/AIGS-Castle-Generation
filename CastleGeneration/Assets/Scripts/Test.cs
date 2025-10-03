using UnityEngine;
using CastleGenerationSimulation;
public class Test : MonoBehaviour
{
    private void Awake()
    {
        Class1 class1 = new Class1();
        Debug.Log(class1.HelloString);

    }   
}